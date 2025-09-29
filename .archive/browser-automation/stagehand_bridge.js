#!/usr/bin/env node
/**
 * Stagehand Bridge - Node.js service for browser automation
 * 
 * This script provides a bridge between Python and Stagehand for browser automation.
 * It receives commands via stdin as JSON and returns results via stdout.
 */

const { Stagehand } = require('@browserbasehq/stagehand');
const readline = require('readline');

class StagehandBridge {
    constructor() {
        this.stagehand = null;
        this.page = null;
        this.isInitialized = false;
        this.setupInputHandler();
    }

    setupInputHandler() {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            terminal: false
        });

        rl.on('line', async (line) => {
            try {
                const command = JSON.parse(line);
                const result = await this.handleCommand(command);
                console.log(JSON.stringify({ success: true, result }));
            } catch (error) {
                console.log(JSON.stringify({ 
                    success: false, 
                    error: error.message,
                    stack: error.stack 
                }));
            }
        });

        rl.on('close', async () => {
            if (this.stagehand) {
                await this.stagehand.close();
            }
            process.exit(0);
        });
    }

    async handleCommand(command) {
        const { action, params = {} } = command;

        switch (action) {
            case 'init':
                return await this.init(params);
            case 'goto':
                return await this.goto(params.url);
            case 'act':
                return await this.act(params.instruction, params.text);
            case 'observe':
                return await this.observe(params.instruction);
            case 'waitForLoadState':
                return await this.waitForLoadState(params.state);
            case 'waitForURL':
                return await this.waitForURL(params.pattern, params.timeout);
            case 'url':
                return await this.getUrl();
            case 'screenshot':
                return await this.takeScreenshot(params.path);
            case 'close':
                return await this.close();
            default:
                throw new Error(`Unknown action: ${action}`);
        }
    }

    async init(options = {}) {
        const defaultOptions = {
            env: "LOCAL", // Use local browser instead of Browserbase
            headless: true,
            localBrowserLaunchOptions: {
                headless: true,
                downloadsPath: "./downloads"
            },
            viewport: { width: 1920, height: 1080 },
            defaultTimeout: 30000,
            logger: (message) => console.error(`[Stagehand] ${message}`)
        };

        const config = { ...defaultOptions, ...options };
        
        this.stagehand = new Stagehand(config);
        await this.stagehand.init();
        this.page = this.stagehand.page; // page is a property, not a method
        this.isInitialized = true;
        
        return { initialized: true };
    }

    async goto(url) {
        if (!this.page) throw new Error('Browser not initialized');
        await this.page.goto(url);
        return { navigated: true, url };
    }

    async act(instruction, text = null) {
        if (!this.stagehand) throw new Error('Browser not initialized');
        
        const params = text ? { text } : {};
        const result = await this.stagehand.act(instruction, params);
        return { acted: true, instruction, result };
    }

    async observe(instruction) {
        if (!this.stagehand) throw new Error('Browser not initialized');
        
        const result = await this.stagehand.observe(instruction);
        return { observed: true, instruction, result };
    }

    async waitForLoadState(state = 'networkidle') {
        if (!this.page) throw new Error('Browser not initialized');
        await this.page.waitForLoadState(state);
        return { waited: true, state };
    }

    async waitForURL(pattern, timeout = 30000) {
        if (!this.page) throw new Error('Browser not initialized');
        await this.page.waitForURL(pattern, { timeout });
        return { waited: true, pattern };
    }

    async getUrl() {
        if (!this.page) throw new Error('Browser not initialized');
        const url = await this.page.url();
        return { url };
    }

    async takeScreenshot(path) {
        if (!this.page) throw new Error('Browser not initialized');
        await this.page.screenshot({ path });
        return { screenshot: true, path };
    }

    async close() {
        if (this.stagehand) {
            await this.stagehand.close();
            this.stagehand = null;
            this.page = null;
            this.isInitialized = false;
        }
        return { closed: true };
    }
}

// Handle process termination gracefully
process.on('SIGINT', async () => {
    console.log(JSON.stringify({ success: true, result: { terminating: true } }));
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log(JSON.stringify({ success: true, result: { terminating: true } }));
    process.exit(0);
});

// Start the bridge
const bridge = new StagehandBridge();
console.log(JSON.stringify({ success: true, result: { ready: true } }));
