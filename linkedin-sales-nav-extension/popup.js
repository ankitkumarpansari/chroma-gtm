// LinkedIn Sales Navigator Company Adder - Popup Script
// Enhanced with continuous looping and skip detection

class SalesNavAdder {
  constructor() {
    this.companies = [];
    this.filteredCompanies = [];
    this.isRunning = false;
    this.currentIndex = 0;
    this.results = [];
    this.stats = {
      processed: 0,
      saved: 0,
      skipped: 0,
      failed: 0
    };
    
    this.init();
  }

  async init() {
    // Load saved state
    await this.loadState();
    
    // Initialize companies (use deduplicated list if available)
    const companyList = typeof COMPANIES_DATA_FINAL !== 'undefined' ? COMPANIES_DATA_FINAL : COMPANIES_DATA;
    this.companies = companyList.map((c, i) => ({
      ...c,
      id: i,
      status: 'pending'
    }));
    
    // Apply saved results to company statuses
    this.applyResultsToCompanies();
    
    // Setup UI
    this.setupEventListeners();
    this.applyFilter();
    this.updateStats();
    this.renderCategories();
    this.renderResults();
    
    console.log(`📊 Loaded ${this.companies.length} companies`);
  }

  async loadState() {
    return new Promise((resolve) => {
      chrome.storage.local.get(['results', 'settings', 'targetList', 'currentIndex'], (data) => {
        this.results = data.results || [];
        this.currentIndex = data.currentIndex || 0;
        this.settings = data.settings || {
          autoSave: true,
          skipSaved: true,
          randomDelay: true,
          continuousMode: true
        };
        // Default to "Ankit Outreach"
        this.targetList = data.targetList || 'Ankit Outreach';
        resolve();
      });
    });
  }

  async saveState() {
    return new Promise((resolve) => {
      chrome.storage.local.set({
        results: this.results,
        settings: this.settings,
        targetList: this.targetList,
        currentIndex: this.currentIndex
      }, resolve);
    });
  }

  applyResultsToCompanies() {
    this.results.forEach(result => {
      const company = this.companies.find(c => c.name === result.name);
      if (company) {
        company.status = result.status;
        company.linkedinUrl = result.linkedinUrl;
        company.skipped = result.skipped;
      }
    });
  }

  setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
    });

    // Filter change
    document.getElementById('priority-filter').addEventListener('change', () => {
      this.applyFilter();
    });

    // Start/Stop buttons
    document.getElementById('start-btn').addEventListener('click', () => this.start());
    document.getElementById('stop-btn').addEventListener('click', () => this.stop());
    document.getElementById('reset-btn').addEventListener('click', () => this.reset());

    // Settings checkboxes
    document.getElementById('auto-save').addEventListener('change', (e) => {
      this.settings.autoSave = e.target.checked;
      this.saveState();
    });
    document.getElementById('skip-saved').addEventListener('change', (e) => {
      this.settings.skipSaved = e.target.checked;
      this.saveState();
    });
    document.getElementById('random-delay').addEventListener('change', (e) => {
      this.settings.randomDelay = e.target.checked;
      this.saveState();
    });

    // Load settings into UI
    document.getElementById('auto-save').checked = this.settings.autoSave;
    document.getElementById('skip-saved').checked = this.settings.skipSaved;
    document.getElementById('random-delay').checked = this.settings.randomDelay;
    document.getElementById('target-list').value = this.targetList;

    // Target list change
    document.getElementById('target-list').addEventListener('change', (e) => {
      this.targetList = e.target.value;
      this.saveState();
    });

    // Results buttons
    document.getElementById('export-btn').addEventListener('click', () => this.exportResults());
    document.getElementById('clear-results').addEventListener('click', () => this.clearResults());
    document.getElementById('clear-all').addEventListener('click', () => this.clearAll());
  }

  switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
  }

  applyFilter() {
    const filter = document.getElementById('priority-filter').value;
    
    if (filter === 'all') {
      this.filteredCompanies = [...this.companies];
    } else if (filter === 'HIGH') {
      this.filteredCompanies = this.companies.filter(c => c.priority === 'HIGH');
    } else if (filter === 'MEDIUM-HIGH') {
      this.filteredCompanies = this.companies.filter(c => 
        c.priority === 'HIGH' || c.priority === 'MEDIUM-HIGH'
      );
    } else if (filter === 'MEDIUM') {
      this.filteredCompanies = this.companies.filter(c => 
        c.priority === 'HIGH' || c.priority === 'MEDIUM-HIGH' || c.priority === 'MEDIUM'
      );
    }

    this.renderCompanyList();
    this.updateStats();
  }

  renderCompanyList() {
    const container = document.getElementById('company-list');
    const batchSize = parseInt(document.getElementById('batch-size').value) || 10;
    
    // Show companies starting from current index
    const startIdx = Math.max(0, this.currentIndex);
    const displayCompanies = this.filteredCompanies.slice(startIdx, startIdx + batchSize);

    if (displayCompanies.length === 0) {
      container.innerHTML = '<div class="empty-state">No companies to display. Try changing the filter or reset progress.</div>';
      return;
    }

    container.innerHTML = displayCompanies.map((company, idx) => `
      <div class="company-item ${company.status}" data-id="${company.id}">
        <div class="status-icon ${company.status}">
          ${this.getStatusIcon(company.status, company.skipped)}
        </div>
        <div class="company-info">
          <div class="company-name">${company.name}</div>
          <div class="company-meta">${company.category} • ${company.valuation || 'N/A'}</div>
        </div>
        <span class="priority-badge ${(company.priority || 'medium').toLowerCase().replace('-', '')}">${company.priority || 'MEDIUM'}</span>
      </div>
    `).join('');
  }

  getStatusIcon(status, skipped) {
    if (skipped) return '⏭️';
    switch (status) {
      case 'pending': return '○';
      case 'processing': return '◐';
      case 'saved': return '✓';
      case 'failed': return '✗';
      default: return '○';
    }
  }

  renderCategories() {
    const categories = {};
    this.companies.forEach(c => {
      if (!categories[c.category]) {
        categories[c.category] = { total: 0, saved: 0, skipped: 0 };
      }
      categories[c.category].total++;
      if (c.status === 'saved') {
        if (c.skipped) {
          categories[c.category].skipped++;
        } else {
          categories[c.category].saved++;
        }
      }
    });

    const container = document.getElementById('category-list');
    container.innerHTML = Object.entries(categories)
      .sort((a, b) => b[1].total - a[1].total)
      .map(([name, stats]) => `
        <div class="category-item">
          <div class="category-header">
            <span class="category-name">${name}</span>
            <span class="category-count">${stats.saved + stats.skipped}/${stats.total}</span>
          </div>
          <div class="category-progress">
            <div class="progress-bar-mini">
              <div class="progress-saved" style="width: ${(stats.saved / stats.total) * 100}%"></div>
              <div class="progress-skipped" style="width: ${(stats.skipped / stats.total) * 100}%"></div>
            </div>
          </div>
        </div>
      `).join('');
  }

  renderResults() {
    const container = document.getElementById('results-list');
    
    if (this.results.length === 0) {
      container.innerHTML = '<p class="empty-state">No results yet. Start adding companies to see results here.</p>';
      return;
    }

    // Show most recent first
    const recentResults = [...this.results].reverse().slice(0, 50);
    
    container.innerHTML = recentResults.map(result => `
      <div class="result-item">
        <span class="result-icon">${result.skipped ? '⏭️' : (result.status === 'saved' ? '✅' : '❌')}</span>
        <span class="result-name">${result.name}</span>
        <span class="result-status ${result.skipped ? 'skipped' : (result.status === 'saved' ? 'success' : 'error')}">
          ${result.skipped ? 'Skipped' : (result.status === 'saved' ? 'Saved' : 'Failed')}
        </span>
      </div>
    `).join('');
  }

  updateStats() {
    const total = this.filteredCompanies.length;
    const pending = this.filteredCompanies.filter(c => c.status === 'pending').length;
    const saved = this.filteredCompanies.filter(c => c.status === 'saved' && !c.skipped).length;
    const skipped = this.filteredCompanies.filter(c => c.skipped).length;
    const failed = this.filteredCompanies.filter(c => c.status === 'failed').length;

    document.getElementById('total-count').textContent = total;
    document.getElementById('pending-count').textContent = pending;
    document.getElementById('saved-count').textContent = saved;
    document.getElementById('failed-count').textContent = failed;

    // Update subtitle with progress
    const subtitle = document.querySelector('.subtitle');
    if (subtitle) {
      const processed = saved + skipped + failed;
      subtitle.textContent = `${processed}/${total} processed • ${saved} saved • ${skipped} skipped`;
    }
  }

  updateProgress(current, total, companyName, status = 'processing') {
    const statusBar = document.getElementById('status-bar');
    const statusText = document.getElementById('status-text');
    const progressFill = document.getElementById('progress-fill');
    const currentCompany = document.getElementById('current-company');
    const currentName = document.getElementById('current-name');

    statusBar.classList.remove('hidden');
    statusText.textContent = `Processing ${current} of ${total}... (${status})`;
    progressFill.style.width = `${(current / total) * 100}%`;

    currentCompany.classList.remove('hidden');
    currentName.textContent = companyName;
  }

  async start() {
    if (this.isRunning) return;

    // Check if we're on Sales Navigator
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab.url.includes('linkedin.com/sales')) {
      alert('Please navigate to LinkedIn Sales Navigator first!\n\nhttps://www.linkedin.com/sales/home');
      return;
    }

    this.isRunning = true;
    document.getElementById('start-btn').classList.add('hidden');
    document.getElementById('stop-btn').classList.remove('hidden');

    const batchSize = parseInt(document.getElementById('batch-size').value) || 10;
    const delay = parseInt(document.getElementById('delay-seconds').value) || 5;
    const listName = document.getElementById('target-list').value || this.targetList;
    
    // Get ALL companies to process (not just a batch - we'll loop through all)
    let toProcess = this.filteredCompanies.filter(c => {
      if (this.settings.skipSaved && (c.status === 'saved' || c.status === 'failed')) {
        return false;
      }
      return true;
    });

    console.log(`🚀 Starting continuous processing of ${toProcess.length} companies`);
    console.log(`📋 Target list: ${listName}`);

    let processedCount = 0;
    let savedCount = 0;
    let skippedCount = 0;
    let failedCount = 0;

    for (let i = 0; i < toProcess.length && this.isRunning; i++) {
      const company = toProcess[i];
      
      processedCount++;
      this.currentIndex = this.filteredCompanies.indexOf(company);
      
      this.updateProgress(processedCount, toProcess.length, company.name, 'searching');
      company.status = 'processing';
      this.renderCompanyList();

      try {
        // Send message to content script to process company
        const result = await this.processCompany(tab.id, company, listName);
        
        if (result.skipped || result.alreadySaved) {
          // Company was already saved - mark as skipped and continue
          company.status = 'saved';
          company.skipped = true;
          skippedCount++;
          console.log(`⏭️ ${company.name} - Already saved, skipping`);
        } else if (result.success) {
          company.status = 'saved';
          company.skipped = false;
          company.linkedinUrl = result.linkedinUrl || '';
          savedCount++;
          console.log(`✅ ${company.name} - Saved successfully`);
        } else {
          company.status = 'failed';
          company.error = result.error;
          failedCount++;
          console.log(`❌ ${company.name} - Failed: ${result.error}`);
        }
        
        // Save result
        const existingResultIndex = this.results.findIndex(r => r.name === company.name);
        const resultEntry = {
          name: company.name,
          category: company.category,
          status: company.status,
          skipped: company.skipped || false,
          linkedinUrl: company.linkedinUrl,
          error: company.error,
          timestamp: new Date().toISOString()
        };
        
        if (existingResultIndex >= 0) {
          this.results[existingResultIndex] = resultEntry;
        } else {
          this.results.push(resultEntry);
        }
        
        await this.saveState();
        
      } catch (error) {
        console.error('Error processing company:', error);
        company.status = 'failed';
        company.error = error.message;
        failedCount++;
      }

      this.renderCompanyList();
      this.updateStats();
      this.renderResults();
      this.renderCategories();

      // Update progress display
      this.updateProgress(
        processedCount, 
        toProcess.length, 
        company.name, 
        company.skipped ? 'skipped' : (company.status === 'saved' ? 'saved' : 'failed')
      );

      // Wait before next company (with random variation if enabled)
      if (i < toProcess.length - 1 && this.isRunning) {
        let actualDelay = delay;
        
        // Shorter delay for skipped companies
        if (company.skipped) {
          actualDelay = Math.max(2, delay / 2);
        }
        
        // Add random variation
        if (this.settings.randomDelay) {
          actualDelay = actualDelay + (Math.random() * 4 - 2);
        }
        
        actualDelay = Math.max(2, actualDelay); // Minimum 2 seconds
        
        console.log(`⏳ Waiting ${actualDelay.toFixed(1)}s before next company...`);
        await this.sleep(actualDelay * 1000);
      }
    }

    // Done!
    console.log(`\n${'='.repeat(50)}`);
    console.log(`🏁 COMPLETED!`);
    console.log(`   Processed: ${processedCount}`);
    console.log(`   Saved: ${savedCount}`);
    console.log(`   Skipped (already saved): ${skippedCount}`);
    console.log(`   Failed: ${failedCount}`);
    console.log(`${'='.repeat(50)}`);

    this.stop();
    
    // Show completion alert
    if (processedCount > 0) {
      alert(`✅ Processing Complete!\n\nProcessed: ${processedCount}\nSaved: ${savedCount}\nSkipped: ${skippedCount}\nFailed: ${failedCount}`);
    }
  }

  async processCompany(tabId, company, listName) {
    return new Promise((resolve, reject) => {
      // Set a timeout for the operation
      const timeout = setTimeout(() => {
        resolve({ success: false, error: 'Timeout waiting for response' });
      }, 60000); // 60 second timeout

      chrome.tabs.sendMessage(tabId, {
        action: 'processCompany',
        company: company,
        listName: listName
      }, (response) => {
        clearTimeout(timeout);
        
        if (chrome.runtime.lastError) {
          console.error('Chrome runtime error:', chrome.runtime.lastError);
          resolve({ success: false, error: chrome.runtime.lastError.message });
        } else {
          resolve(response || { success: false, error: 'No response from content script' });
        }
      });
    });
  }

  stop() {
    this.isRunning = false;
    document.getElementById('start-btn').classList.remove('hidden');
    document.getElementById('stop-btn').classList.add('hidden');
    document.getElementById('status-bar').classList.add('hidden');
    document.getElementById('current-company').classList.add('hidden');
    
    // Save current progress
    this.saveState();
  }

  reset() {
    if (this.isRunning) {
      this.stop();
    }
    
    // Only reset pending status, keep saved/skipped status
    this.filteredCompanies.forEach(c => {
      if (c.status === 'failed') {
        c.status = 'pending';
      }
    });
    
    this.currentIndex = 0;
    this.saveState();
    this.renderCompanyList();
    this.updateStats();
  }

  clearResults() {
    if (confirm('Clear all results? This will reset progress tracking.')) {
      this.results = [];
      this.currentIndex = 0;
      this.companies.forEach(c => {
        c.status = 'pending';
        c.skipped = false;
        c.linkedinUrl = '';
        c.error = '';
      });
      this.saveState();
      this.applyFilter();
      this.renderResults();
      this.renderCategories();
    }
  }

  clearAll() {
    if (confirm('Are you sure you want to reset EVERYTHING? This will clear all results and progress.')) {
      this.results = [];
      this.currentIndex = 0;
      this.companies.forEach(c => {
        c.status = 'pending';
        c.skipped = false;
        c.linkedinUrl = '';
        c.error = '';
      });
      this.saveState();
      this.applyFilter();
      this.renderResults();
      this.renderCategories();
    }
  }

  exportResults() {
    const exportData = {
      exportDate: new Date().toISOString(),
      targetList: this.targetList,
      summary: {
        total: this.companies.length,
        saved: this.results.filter(r => r.status === 'saved' && !r.skipped).length,
        skipped: this.results.filter(r => r.skipped).length,
        failed: this.results.filter(r => r.status === 'failed').length
      },
      results: this.results
    };
    
    const data = JSON.stringify(exportData, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `linkedin-companies-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    
    URL.revokeObjectURL(url);
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new SalesNavAdder();
});
