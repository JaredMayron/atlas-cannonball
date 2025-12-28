#!/usr/bin/env node
import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';

// --- CONFIGURATION ---
const DASHBOARDS = [
    {
        name: 'cash-reserves',
        url: 'https://www.evidence.studio/org_01KCNDDX3PYPNT5HNPSZQXZPKV/net-worth-dashboard/cash-reserves'
    },
    {
        name: 'net-worth',
        url: 'https://www.evidence.studio/org_01KCNDDX3PYPNT5HNPSZQXZPKV/net-worth-dashboard/net-worth'
    }
];

const VIEWPORT = { width: 1920, height: 1080 };
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const USER_DATA_DIR = path.join(__dirname, 'chrome-profile');

// --- MAIN SCRIPT ---
(async () => {
    console.log('--- Starting Screenshot Automation (Headless Chrome/Chromium) ---');

    // 1. Launch Browser
    // We use a persistent profile so you don't have to log in every time.
    // We'll start in "headed" mode first to let you log in if needed.
    const browser = await puppeteer.launch({
        headless: false, // We'll start headed to check for session
        userDataDir: USER_DATA_DIR,
        defaultViewport: null,
        args: ['--start-maximized']
    });

    try {
        const page = await browser.newPage();
        await page.setViewport(VIEWPORT);

        // 2. Auth Check
        const firstDashboard = DASHBOARDS[0];
        console.log(`Navigating to: ${firstDashboard.url}`);
        await page.goto(firstDashboard.url);

        console.log('⏳ Waiting for you to finish logging in...');
        console.log('The script will proceed automatically once you land on the dashboard.');

        // 3. Wait for the EXACT URL from the README to be reached
        // We wait for the URL to contain the specific dashboard path AND ensure we aren't on an auth page.
        await page.waitForFunction(
            (expectedUrl) => {
                const currentHref = window.location.href;
                // Check if current URL contains our target dashboard URL 
                // and we've successfully moved away from any auth/login domains
                const isOnTarget = currentHref.startsWith(expectedUrl);
                const isNotAuth = !currentHref.includes('google.com') && !currentHref.includes('auth');

                return isOnTarget && isNotAuth;
            },
            { timeout: 0 },
            firstDashboard.url
        );

        console.log('✅ Destination URL reached! Waiting 15 seconds for all charts to process data...');
        await new Promise(r => setTimeout(r, 15000));

        // 4. Capture Loop
        for (const dashboard of DASHBOARDS) {
            console.log(`Capturing: ${dashboard.name}...`);

            if (page.url() !== dashboard.url) {
                await page.goto(dashboard.url, { waitUntil: 'networkidle0', timeout: 60000 });
                await new Promise(r => setTimeout(r, 5000));
            }

            const filename = `${dashboard.name}.png`;
            const filePath = path.join(__dirname, filename);

            await page.screenshot({ path: filePath, fullPage: true });
            console.log(`✅ Saved: ${filePath}`);
        }

    } catch (error) {
        console.error('❌ Error during capture:', error);
    } finally {
        await browser.close();
        console.log('--- Capture Complete ---');
    }
})();
