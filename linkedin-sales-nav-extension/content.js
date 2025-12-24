// LinkedIn Sales Navigator Content Script - ENHANCED VERSION
// Handles already-saved companies and continuous looping
// Target list: Ankit Outreach

console.log('🎯 Sales Nav Adder: Content script loaded on', window.location.href);

const DEFAULT_LIST = "Ankit Outreach";

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('📨 Received message:', request);
  
  if (request.action === 'processCompany') {
    handleProcessCompany(request.company, request.listName || DEFAULT_LIST)
      .then(result => {
        console.log('✅ Result:', result);
        sendResponse(result);
      })
      .catch(error => {
        console.error('❌ Error:', error);
        sendResponse({ success: false, error: error.message, skipped: false });
      });
    return true; // Keep channel open for async response
  }
});

async function handleProcessCompany(company, listName) {
  const companyName = company.name;
  console.log(`\n${'='.repeat(50)}`);
  console.log(`🔍 PROCESSING: ${companyName}`);
  console.log(`📋 Target List: ${listName}`);
  console.log(`${'='.repeat(50)}`);
  
  showStatus(`Searching for ${companyName}...`);

  // Step 1: Go to search page
  const searchUrl = `https://www.linkedin.com/sales/search/company?query=(keywords%3A${encodeURIComponent(companyName)})`;
  console.log('📍 Navigating to:', searchUrl);
  window.location.href = searchUrl;

  // Wait for navigation and page load
  await sleep(4000);
  
  console.log('📄 Page loaded, current URL:', window.location.href);
  
  // Step 2: Wait for results to load
  console.log('⏳ Waiting for search results...');
  const hasResults = await waitForResults();
  
  if (!hasResults) {
    showStatus(`❌ No results found for ${companyName}`, 3000);
    return { success: false, error: 'No search results found', skipped: false };
  }
  
  // Step 3: Log page structure for debugging
  logPageStructure();
  
  // Step 4: Check if the first result is already saved to our list
  console.log('🔍 Checking if company is already saved...');
  const alreadySaved = await checkIfAlreadySaved(listName);
  
  if (alreadySaved) {
    console.log(`⏭️ ${companyName} is ALREADY SAVED to ${listName} - skipping!`);
    showStatus(`⏭️ ${companyName} already saved - skipping`, 2000);
    return { success: true, skipped: true, alreadySaved: true, message: 'Already saved to list' };
  }
  
  // Step 5: Select the first result
  console.log('☑️ Attempting to select first result...');
  showStatus(`Selecting ${companyName}...`);
  const selected = await trySelectFirstResult();
  
  if (!selected) {
    showStatus(`❌ Could not select ${companyName}`, 3000);
    return { success: false, error: 'Could not select first result', skipped: false };
  }
  
  await sleep(1000);
  
  // Step 6: Click Save to list button
  console.log('💾 Attempting to click Save to list...');
  showStatus(`Saving ${companyName} to ${listName}...`);
  const saveClicked = await tryClickSaveToList();
  
  if (!saveClicked) {
    showStatus(`❌ Save to list button not found`, 3000);
    return { success: false, error: 'Could not find Save to list button', skipped: false };
  }
  
  await sleep(1500);
  
  // Step 7: Select the target list (Ankit Outreach)
  console.log(`📋 Selecting list: ${listName}`);
  const listSelected = await trySelectList(listName);
  
  if (!listSelected) {
    // Try clicking outside to close any open dropdown
    document.body.click();
    showStatus(`⚠️ List selection may have failed`, 2000);
  }
  
  await sleep(500);
  
  // Close any open dropdowns
  document.body.click();
  await sleep(300);
  
  // Deselect the checkbox to clean up
  await deselectAll();
  
  showStatus(`✅ ${companyName} added to ${listName}!`, 3000);
  console.log(`✅ DONE: ${companyName} saved to ${listName}`);
  
  return { success: true, skipped: false, linkedinUrl: window.location.href };
}

async function waitForResults() {
  for (let i = 0; i < 30; i++) {
    // Look for various signs of results loading
    const hasResults = 
      document.querySelector('[class*="search-results"]') ||
      document.querySelector('[class*="result-list"]') ||
      document.querySelector('[data-anonymize="company-name"]') ||
      document.querySelector('[class*="artdeco-entity-lockup"]') ||
      document.querySelectorAll('input[type="checkbox"]').length > 1;
    
    // Also check for "no results" message
    const noResults = 
      document.body.innerText.includes('No results found') ||
      document.body.innerText.includes('0 results') ||
      document.querySelector('[class*="no-results"]');
    
    if (noResults) {
      console.log('⚠️ No results found for this search');
      return false;
    }
    
    if (hasResults) {
      console.log('✅ Results detected');
      await sleep(500); // Extra wait for full render
      return true;
    }
    await sleep(500);
  }
  console.log('⚠️ Timeout waiting for results');
  return false;
}

async function checkIfAlreadySaved(targetListName) {
  // Method 1: Look for "Saved" indicator on the first result
  const savedIndicators = document.querySelectorAll('[class*="saved"], [class*="Saved"], [aria-label*="saved"], [aria-label*="Saved"]');
  console.log(`  Found ${savedIndicators.length} potential saved indicators`);
  
  // Method 2: Check for list badges/tags showing the company is in a list
  const listBadges = document.querySelectorAll('[class*="list-badge"], [class*="entity-list"], [class*="saved-to"]');
  console.log(`  Found ${listBadges.length} list badges`);
  
  // Method 3: Look for the specific list name in the first result row
  const firstResult = document.querySelector('li[class*="result"], [class*="search-result"], [class*="entity-result"]');
  if (firstResult) {
    const resultText = firstResult.innerText || '';
    // Check if our target list name appears in the result
    if (resultText.includes(targetListName) || resultText.includes('Ankit Outreach')) {
      console.log(`  ✅ Found "${targetListName}" in first result - already saved!`);
      return true;
    }
    
    // Check for generic "Saved" text near the result
    if (resultText.includes('Saved to list') || resultText.includes('In list')) {
      console.log('  ✅ Found "Saved to list" indicator');
      return true;
    }
  }
  
  // Method 4: Check button states - if "Save to list" shows as already saved
  const allButtons = document.querySelectorAll('button');
  for (const btn of allButtons) {
    const text = (btn.textContent || '').trim().toLowerCase();
    const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
    const ariaPressed = btn.getAttribute('aria-pressed');
    
    // If there's a "Saved" button or the save button shows as pressed/active
    if ((text.includes('saved') && !text.includes('save to')) || 
        ariaLabel.includes('saved to') ||
        (ariaPressed === 'true' && (text.includes('list') || ariaLabel.includes('list')))) {
      console.log(`  ✅ Found saved button state: "${text}" pressed=${ariaPressed}`);
      return true;
    }
  }
  
  // Method 5: Select the first result and check the Save button state
  const checkbox = await getFirstResultCheckbox();
  if (checkbox && !checkbox.checked) {
    checkbox.click();
    await sleep(800);
    
    // Now check if the Save to list button shows "Saved" state
    const saveBtn = await findSaveToListButton();
    if (saveBtn) {
      const btnText = (saveBtn.textContent || '').toLowerCase();
      const btnAriaLabel = (saveBtn.getAttribute('aria-label') || '').toLowerCase();
      
      // Check if it says "Saved" instead of "Save"
      if (btnText.includes('saved') || btnAriaLabel.includes('saved')) {
        console.log('  ✅ Save button shows "Saved" state');
        // Deselect and return
        checkbox.click();
        await sleep(300);
        return true;
      }
      
      // Click the save button to see the dropdown
      saveBtn.click();
      await sleep(800);
      
      // Check if our list shows a checkmark or is already selected
      const listItems = document.querySelectorAll('[role="option"], [role="menuitem"], [class*="dropdown"] li');
      for (const item of listItems) {
        const itemText = (item.textContent || '').trim();
        if (itemText.includes(targetListName) || itemText.includes('Ankit Outreach')) {
          // Check for checkmark or selected state
          const hasCheckmark = item.querySelector('svg, [class*="check"], [class*="selected"]');
          const isSelected = item.getAttribute('aria-selected') === 'true' || 
                            item.classList.toString().includes('selected');
          
          if (hasCheckmark || isSelected) {
            console.log(`  ✅ List "${targetListName}" shows as already selected`);
            // Close dropdown and deselect
            document.body.click();
            await sleep(300);
            checkbox.click();
            await sleep(300);
            return true;
          }
        }
      }
      
      // Close the dropdown
      document.body.click();
      await sleep(300);
    }
    
    // Deselect the checkbox
    if (checkbox.checked) {
      checkbox.click();
      await sleep(300);
    }
  }
  
  console.log('  ℹ️ Company does not appear to be saved yet');
  return false;
}

async function getFirstResultCheckbox() {
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  
  for (let i = 0; i < checkboxes.length; i++) {
    const cb = checkboxes[i];
    const ariaLabel = (cb.getAttribute('aria-label') || '').toLowerCase();
    const id = (cb.id || '').toLowerCase();
    
    // Skip "select all" type checkboxes
    if (ariaLabel.includes('select all') || id.includes('select-all') || id.includes('selectall')) {
      continue;
    }
    
    // Return the first non-select-all checkbox
    return cb;
  }
  
  return null;
}

async function findSaveToListButton() {
  const allButtons = document.querySelectorAll('button');
  
  for (const btn of allButtons) {
    const text = (btn.textContent || '').trim().toLowerCase();
    const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
    
    if (text.includes('save to list') || 
        text.includes('add to list') ||
        ariaLabel.includes('save to list') ||
        ariaLabel.includes('add to list') ||
        (text.includes('save') && text.includes('list'))) {
      return btn;
    }
  }
  
  return null;
}

function logPageStructure() {
  console.log('\n📊 PAGE STRUCTURE ANALYSIS:');
  
  // Log all checkboxes
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  console.log(`  Checkboxes found: ${checkboxes.length}`);
  
  // Log save-related buttons
  const buttons = document.querySelectorAll('button');
  let saveButtons = 0;
  buttons.forEach((btn) => {
    const text = (btn.textContent || '').trim().toLowerCase();
    const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
    if (text.includes('save') || text.includes('list') ||
        ariaLabel.includes('save') || ariaLabel.includes('list')) {
      saveButtons++;
      console.log(`  Save button: "${text.substring(0, 40)}" aria="${ariaLabel.substring(0, 40)}"`);
    }
  });
  console.log(`  Total save-related buttons: ${saveButtons}`);
}

async function trySelectFirstResult() {
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  console.log(`  Found ${checkboxes.length} checkboxes`);
  
  for (let i = 0; i < checkboxes.length; i++) {
    const cb = checkboxes[i];
    const ariaLabel = (cb.getAttribute('aria-label') || '').toLowerCase();
    const id = (cb.id || '').toLowerCase();
    
    // Skip "select all" type checkboxes
    if (ariaLabel.includes('select all') || id.includes('select-all') || id.includes('selectall')) {
      console.log(`  Skipping checkbox ${i} (select all)`);
      continue;
    }
    
    if (!cb.checked) {
      console.log(`  Clicking checkbox ${i}`);
      cb.click();
      await sleep(500);
      
      if (cb.checked) {
        console.log(`  ✅ Checkbox ${i} is now checked`);
        return true;
      }
    } else {
      console.log(`  Checkbox ${i} already checked`);
      return true;
    }
  }
  
  // Method 2: Try clicking labels
  const labels = document.querySelectorAll('label');
  for (const label of labels) {
    const forAttr = label.getAttribute('for') || '';
    if (forAttr && !forAttr.toLowerCase().includes('select-all')) {
      console.log(`  Trying to click label for="${forAttr}"`);
      label.click();
      await sleep(500);
      return true;
    }
  }
  
  console.log('  ❌ No checkbox could be selected');
  return false;
}

async function tryClickSaveToList() {
  const allButtons = document.querySelectorAll('button');
  console.log(`  Searching through ${allButtons.length} buttons...`);
  
  // First pass: exact match
  for (const btn of allButtons) {
    const text = (btn.textContent || btn.innerText || '').trim().toLowerCase();
    const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
    
    if (text === 'save to list' || 
        ariaLabel === 'save to list' ||
        text.includes('save to list') ||
        ariaLabel.includes('save to list')) {
      console.log(`  Found exact match button: "${text}"`);
      btn.click();
      console.log('  ✅ Clicked Save to list button');
      return true;
    }
  }
  
  // Second pass: partial match
  for (const btn of allButtons) {
    const text = (btn.textContent || '').trim().toLowerCase();
    const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
    
    if ((text.includes('save') && text.includes('list')) || 
        (ariaLabel.includes('save') && ariaLabel.includes('list')) ||
        (text.includes('add') && text.includes('list'))) {
      console.log(`  Found partial match button: "${text}"`);
      btn.click();
      return true;
    }
  }
  
  // Third pass: look in action bars
  const actionButtons = document.querySelectorAll('[class*="action"] button, [class*="toolbar"] button, [class*="bulk"] button');
  console.log(`  Found ${actionButtons.length} action bar buttons`);
  
  for (const btn of actionButtons) {
    const text = (btn.textContent || '').toLowerCase();
    if (text.includes('list') || text.includes('save')) {
      console.log(`  Found action bar button: "${text.substring(0, 30)}"`);
      btn.click();
      return true;
    }
  }
  
  console.log('  ❌ Save to list button not found');
  return false;
}

async function trySelectList(listName) {
  await sleep(1000);
  
  console.log(`  Looking for list: "${listName}"`);
  
  // Find all clickable list options
  const selectors = [
    '[role="option"]',
    '[role="menuitem"]',
    '[role="listitem"]',
    '[class*="dropdown"] li',
    '[class*="dropdown"] button',
    '[class*="popover"] li',
    '[class*="overlay"] li',
    '[class*="menu"] li'
  ];
  
  const options = document.querySelectorAll(selectors.join(', '));
  console.log(`  Found ${options.length} list options`);
  
  // First: look for exact match to our target list
  for (const opt of options) {
    const text = (opt.textContent || '').trim();
    
    if (text.includes(listName) || text.includes('Ankit Outreach') || text.includes('Ankit')) {
      if (opt.offsetParent !== null) { // Check if visible
        console.log(`  ✅ Found target list: "${text.substring(0, 50)}"`);
        opt.click();
        return true;
      }
    }
  }
  
  // Second: search entire document for clickable elements with our list name
  const allElements = document.querySelectorAll('*');
  for (const el of allElements) {
    const text = (el.textContent || '').trim();
    
    if ((text.includes(listName) || text.includes('Ankit Outreach')) && 
        text.length < 100) { // Avoid clicking large containers
      const isClickable = el.tagName === 'BUTTON' || 
                         el.tagName === 'LI' || 
                         el.tagName === 'A' ||
                         el.tagName === 'DIV' ||
                         el.getAttribute('role') === 'option' ||
                         el.getAttribute('role') === 'menuitem' ||
                         el.getAttribute('tabindex') !== null ||
                         el.onclick !== null;
      
      if (isClickable && el.offsetParent !== null) {
        console.log(`  Found clickable element with list name: "${text.substring(0, 50)}"`);
        el.click();
        return true;
      }
    }
  }
  
  console.log(`  ⚠️ Could not find list "${listName}"`);
  return false;
}

async function deselectAll() {
  const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
  for (const cb of checkboxes) {
    const ariaLabel = (cb.getAttribute('aria-label') || '').toLowerCase();
    if (!ariaLabel.includes('select all')) {
      cb.click();
      await sleep(200);
    }
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Enhanced status indicator with progress
function showStatus(message, duration = 0) {
  let indicator = document.getElementById('sn-adder-status');
  
  if (!indicator) {
    indicator = document.createElement('div');
    indicator.id = 'sn-adder-status';
    indicator.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: white;
      padding: 16px 24px;
      border-radius: 12px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      font-weight: 500;
      z-index: 999999;
      box-shadow: 0 4px 20px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.1);
      display: none;
      max-width: 350px;
      backdrop-filter: blur(10px);
    `;
    document.body.appendChild(indicator);
  }
  
  // Add icon based on message content
  let icon = '🔄';
  if (message.includes('✅')) icon = '';
  else if (message.includes('❌')) icon = '';
  else if (message.includes('⏭️')) icon = '';
  else if (message.includes('Searching')) icon = '🔍';
  else if (message.includes('Saving')) icon = '💾';
  else if (message.includes('Selecting')) icon = '☑️';
  
  indicator.textContent = icon ? `${icon} ${message.replace(/[✅❌⏭️]/g, '').trim()}` : message;
  indicator.style.display = 'block';
  
  if (duration > 0) {
    setTimeout(() => {
      indicator.style.display = 'none';
    }, duration);
  }
}

// Ready message
console.log('🎯 Sales Nav Adder: Enhanced version loaded!');
console.log('📋 Default list: ' + DEFAULT_LIST);
console.log('💡 Open DevTools Console (F12) to see detailed logs.');
