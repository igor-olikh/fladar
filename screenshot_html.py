#!/usr/bin/env python3
"""
Script to take a screenshot of the HTML file
"""
import os
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Installing...")
    os.system("pip install playwright")
    os.system("playwright install chromium")
    from playwright.sync_api import sync_playwright

def take_screenshot(html_file: str, output_file: str = "flight_results_screenshot.png"):
    """Take a screenshot of the HTML file"""
    html_path = os.path.abspath(html_file)
    
    if not os.path.exists(html_path):
        print(f"Error: HTML file not found: {html_path}")
        return False
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Load the HTML file
        page.goto(f"file://{html_path}")
        
        # Wait for content to load
        page.wait_for_load_state("networkidle")
        
        # Take a full page screenshot
        page.screenshot(path=output_file, full_page=True)
        
        browser.close()
        
        print(f"Screenshot saved to: {output_file}")
        return True

if __name__ == "__main__":
    html_file = sys.argv[1] if len(sys.argv) > 1 else "flight_results.html"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "flight_results_screenshot.png"
    
    take_screenshot(html_file, output_file)

