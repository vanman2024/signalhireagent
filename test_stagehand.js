const { Stagehand } = require('@browserbasehq/stagehand');

async function testStagehand() {
    console.log("Testing Stagehand...");
    
    const stagehand = new Stagehand({
        env: "LOCAL"
    });
    
    try {
        await stagehand.init();
        console.log("✅ Stagehand initialized");
        
        const page = stagehand.page;
        await page.goto("https://httpbin.org/get");
        
        console.log("✅ Navigation successful");
        console.log("Current URL:", page.url());
        
    } catch (error) {
        console.error("❌ Error:", error.message);
    } finally {
        await stagehand.close();
    }
}

testStagehand();
