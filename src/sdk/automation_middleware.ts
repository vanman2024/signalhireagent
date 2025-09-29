/**
 * Claude Code SDK Middleware Service
 * Intelligent orchestration layer between SignalHire CLI and Airtable
 */

import { createSdkMcpServer, tool } from "@anthropic-ai/claude-code";
import { z } from "zod";
import Airtable from "airtable";
import axios from "axios";

// Configuration schema
const ConfigSchema = z.object({
  signalhire: z.object({
    apiKey: z.string(),
    baseUrl: z.string().default("https://api.signalhire.com"),
  }),
  airtable: z.object({
    apiKey: z.string(),
    baseId: z.string(),
    tables: z.object({
      contacts: z.string().default("tbl0uFVaAfcNjT2rS"),
      industries: z.string().default("tblIndustries"),
      searchSessions: z.string().default("tblqmpcDHfG5pZCWh"),
    }),
  }),
});

export const automationMiddleware = createSdkMcpServer({
  name: "signalhire-airtable-middleware",
  version: "1.0.0",
  description: "Intelligent middleware for SignalHire to Airtable automation",

  tools: [
    tool(
      "intelligent_search_and_sync",
      "Intelligently search SignalHire and sync to Airtable with deduplication",
      {
        searchParams: z.object({
          title: z.string().optional(),
          keywords: z.string().optional(),
          location: z.string().optional(),
          industry: z.string().optional(),
        }),
        syncOptions: z.object({
          checkDuplicates: z.boolean().default(true),
          enrichIndustries: z.boolean().default(true),
          linkRecords: z.boolean().default(true),
        }),
      },
      async (args) => {
        // Step 1: Check existing Airtable records for duplicates
        const existingContacts = await checkExistingContacts(args.searchParams);

        // Step 2: Perform SignalHire search with exclusions
        const searchResults = await performSignalHireSearch(
          args.searchParams,
          existingContacts.map(c => c.signalhireId)
        );

        // Step 3: Enrich with industry data
        const enrichedResults = args.syncOptions.enrichIndustries
          ? await enrichWithIndustries(searchResults)
          : searchResults;

        // Step 4: Create linked records structure
        const linkedData = args.syncOptions.linkRecords
          ? await createLinkedRecordsStructure(enrichedResults)
          : enrichedResults;

        // Step 5: Sync to Airtable with proper field mapping
        const syncResult = await syncToAirtable(linkedData);

        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              searched: searchResults.length,
              duplicatesSkipped: existingContacts.length,
              synced: syncResult.created,
              errors: syncResult.errors,
            }, null, 2)
          }]
        };
      }
    ),

    tool(
      "fix_search_patterns",
      "Validate and fix search patterns for Heavy Equipment Technicians",
      {
        pattern: z.string(),
        testSize: z.number().default(5),
      },
      async (args) => {
        // Validate Boolean operators
        const validation = validateBooleanQuery(args.pattern);

        // Test search with small sample
        const testResults = await testSearchPattern(args.pattern, args.testSize);

        // Analyze results for quality
        const analysis = analyzeSearchQuality(testResults);

        // Suggest improvements
        const suggestions = generatePatternSuggestions(analysis);

        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              validation,
              testResults: testResults.length,
              quality: analysis,
              suggestions,
            }, null, 2)
          }]
        };
      }
    ),

    tool(
      "manage_linked_records",
      "Set up and manage linked record relationships in Airtable",
      {
        sourceTable: z.string(),
        targetTable: z.string(),
        linkField: z.string(),
        relationshipType: z.enum(["one-to-many", "many-to-many"]),
      },
      async (args) => {
        const base = new Airtable({ apiKey: process.env.AIRTABLE_API_KEY })
          .base(process.env.AIRTABLE_BASE_ID);

        // Create or update link field
        const linkResult = await createLinkField(
          base,
          args.sourceTable,
          args.targetTable,
          args.linkField,
          args.relationshipType
        );

        return {
          content: [{
            type: "text",
            text: `Link field "${args.linkField}" configured successfully`
          }]
        };
      }
    ),

    tool(
      "import_industry_data",
      "Import industry classifications and map to contacts",
      {
        sourceFile: z.string().optional(),
        mappingRules: z.object({
          jobTitlePatterns: z.array(z.string()),
          companyPatterns: z.array(z.string()),
        }).optional(),
      },
      async (args) => {
        // Load industry data
        const industries = await loadIndustryData(args.sourceFile);

        // Create industry records in Airtable
        const createdIndustries = await createIndustryRecords(industries);

        // Map existing contacts to industries
        const mappingResult = await mapContactsToIndustries(
          args.mappingRules || defaultMappingRules
        );

        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              industriesCreated: createdIndustries.length,
              contactsMapped: mappingResult.mapped,
              unmapped: mappingResult.unmapped,
            }, null, 2)
          }]
        };
      }
    ),

    tool(
      "validate_data_quality",
      "Check data quality and fix common issues",
      {
        checkTypes: z.array(z.enum([
          "duplicates",
          "missingFields",
          "invalidEmails",
          "locationParsing",
          "industryMapping",
        ])),
        autoFix: z.boolean().default(false),
      },
      async (args) => {
        const issues: any[] = [];

        for (const checkType of args.checkTypes) {
          const checkResult = await performDataQualityCheck(checkType);
          issues.push(...checkResult.issues);

          if (args.autoFix && checkResult.fixable) {
            await applyDataFixes(checkResult.fixes);
          }
        }

        return {
          content: [{
            type: "text",
            text: JSON.stringify({
              totalIssues: issues.length,
              fixed: args.autoFix ? issues.filter(i => i.fixed).length : 0,
              recommendations: generateDataQualityRecommendations(issues),
            }, null, 2)
          }]
        };
      }
    ),
  ],
});

// Helper functions
async function checkExistingContacts(searchParams: any) {
  const base = new Airtable({ apiKey: process.env.AIRTABLE_API_KEY })
    .base(process.env.AIRTABLE_BASE_ID);

  const formula = buildAirtableFormula(searchParams);
  const records = await base('Contacts').select({
    filterByFormula: formula,
    fields: ['SignalHire ID', 'Full Name', 'Email'],
  }).all();

  return records.map(r => ({
    signalhireId: r.get('SignalHire ID'),
    fullName: r.get('Full Name'),
    email: r.get('Email'),
  }));
}

async function performSignalHireSearch(params: any, excludeIds: string[]) {
  const response = await axios.post(
    'https://api.signalhire.com/v1/search',
    {
      ...params,
      exclude_ids: excludeIds,
    },
    {
      headers: {
        'Authorization': `Bearer ${process.env.SIGNALHIRE_API_KEY}`,
      },
    }
  );

  return response.data.results;
}

async function enrichWithIndustries(contacts: any[]) {
  // Implementation for industry enrichment
  return contacts.map(contact => ({
    ...contact,
    industry: detectIndustryFromJobTitle(contact.jobTitle),
    industryConfidence: 0.85,
  }));
}

async function createLinkedRecordsStructure(contacts: any[]) {
  // Set up proper linked record relationships
  return contacts.map(contact => ({
    ...contact,
    linkedRecords: {
      industry: contact.industry ? [contact.industry] : [],
      searchSession: contact.searchSessionId ? [contact.searchSessionId] : [],
    },
  }));
}

async function syncToAirtable(data: any[]) {
  const base = new Airtable({ apiKey: process.env.AIRTABLE_API_KEY })
    .base(process.env.AIRTABLE_BASE_ID);

  const results = { created: 0, errors: [] };

  for (const record of data) {
    try {
      await base('Contacts').create(record);
      results.created++;
    } catch (error: any) {
      results.errors.push(error.message);
    }
  }

  return results;
}

function validateBooleanQuery(query: string): any {
  const issues = [];

  // Check for balanced parentheses
  const openParens = (query.match(/\(/g) || []).length;
  const closeParens = (query.match(/\)/g) || []).length;
  if (openParens !== closeParens) {
    issues.push("Unbalanced parentheses");
  }

  // Check for valid operators
  const validOperators = ['AND', 'OR', 'NOT'];
  const operators = query.match(/\b(AND|OR|NOT)\b/g) || [];

  return {
    valid: issues.length === 0,
    issues,
    operators: operators.length,
  };
}

function detectIndustryFromJobTitle(jobTitle: string): string {
  const industryMap = {
    'Heavy Equipment': ['technician', 'mechanic', 'diesel', 'equipment'],
    'Construction': ['construction', 'builder', 'contractor'],
    'Technology': ['software', 'developer', 'engineer', 'programmer'],
    // Add more mappings
  };

  for (const [industry, keywords] of Object.entries(industryMap)) {
    if (keywords.some(kw => jobTitle.toLowerCase().includes(kw))) {
      return industry;
    }
  }

  return 'General';
}

// Export for use in CLI
export default automationMiddleware;