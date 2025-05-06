<template>
    <div class="performance-dashboard">
      <Header />
      <sidebar />
      <div class="app-container">
        <div class="dashboard-container">
          <div class="header-section">
            <h2 class="section-title">Performance Metrics</h2>
          </div>
          
          <div class="dashboard-grid">
            <!-- Current Metrics Cards -->
            <div class="card stats">
    <h3>Average Transaction Speed</h3>
    <div class="stat-value">
      {{ metrics.current_metrics.avg_transaction_time ? 
          metrics.current_metrics.avg_transaction_time.toFixed(2) + ' ms' : 
          'No data' }}
    </div>
    <div class="stat-change" 
         :class="getTransactionSpeedClass(metrics.current_metrics.avg_transaction_time)">
      {{ getTransactionSpeedStatus(metrics.current_metrics.avg_transaction_time) }}
    </div>
  </div>
            <div class="card stats">
              <h3>Error Rate</h3>
              <div class="stat-value">{{ metrics.current_metrics.error_rate.toFixed(2) }}%</div>
              <div class="stat-change" :class="getErrorStatusClass(metrics.current_metrics.error_rate)">
                {{ getErrorRateStatus(metrics.current_metrics.error_rate) }}
              </div>
            </div>
            
            <div class="card stats">
    <h3>Stock Update Speed</h3>
    <div class="stat-value">
      {{ metrics.current_metrics.avg_stock_update_time ? 
          metrics.current_metrics.avg_stock_update_time.toFixed(2) + ' ms' : 
          'No data' }}
    </div>
    <div class="stat-change" 
         :class="getStockUpdateSpeedClass(metrics.current_metrics.avg_stock_update_time)">
      {{ getStockUpdateSpeedStatus(metrics.current_metrics.avg_stock_update_time) }}
    </div>
  </div>

  <div class="card stats">
  <h3>Recent Stock Update Times</h3>
  <ul v-if="metrics.stock_update_times && metrics.stock_update_times.length">
    <li v-for="(t, idx) in metrics.stock_update_times" :key="idx">
      {{ t.execution_time_ms.toFixed(2) }} ms 
      <span v-if="t.product_id">for Product ID: {{ t.product_id }}</span>
      at {{ formatDate(t.timestamp) }}
    </li>
  </ul>
  <div v-else>No recent stock updates.</div>
</div>

            <!-- Transaction Times Chart -->
            <div class="card chart">
              <h3>Response Times (ms)</h3>
              <div class="chart-container">
                <canvas ref="responseTimeChart"></canvas>
              </div>
            </div>
            
            <!-- Database Stats -->
            <div class="card db-stats">
              <h3>Database Performance</h3>
              <div v-if="isLoadingDbStats" class="loading-indicator">
                <i class="pi pi-spin pi-spinner"></i> Loading database stats...
              </div>
              <div v-else-if="dbStatsError" class="error-message">
                {{ dbStatsError }}
              </div>
              <div v-else>
                <div class="stat-grid">
                  <div class="db-stat-item">
                    <span class="label">Connection Usage</span>
                    <span class="value">{{ dbStats.connection_stats.connection_usage_percent.toFixed(2) }}%</span>
                  </div>
                  <div class="db-stat-item">
                    <span class="label">Uptime</span>
                    <span class="value">{{ dbStats.uptime.readable }}</span>
                  </div>
                  <div class="db-stat-item">
                    <span class="label">Active Connections</span>
                    <span class="value">{{ dbStats.connection_stats.active_connections }} / {{ dbStats.connection_stats.max_connections }}</span>
                  </div>
                </div>
                
                <h4>Database Tables</h4>
                <table class="db-table">
                  <thead>
                    <tr>
                      <th>Table</th>
                      <th>Rows</th>
                      <th>Size (MB)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="table in dbStats.table_stats.slice(0, 5)" :key="table.table_name">
                      <td>{{ table.table_name }}</td>
                      <td>{{ table.rows }}</td>
                      <td>{{ table.total_size_mb.toFixed(2) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <!-- Backup Status -->
            <div class="card backup-status">
              <h3>Backup Status</h3>
              <div v-if="isLoadingBackup" class="loading-indicator">
                <i class="pi pi-spin pi-spinner"></i> Loading backup information...
              </div>
              <div v-else-if="backupError" class="error-message">
                {{ backupError }}
              </div>
              <div v-else class="backup-info">
                <div class="last-backup">
                  <h4>Last Backup</h4>
                  <p>Date: {{ formatDate(backupStatus.last_backup.timestamp) }}</p>
                  <p>Status: <span :class="backupStatus.last_backup.status">{{ backupStatus.last_backup.status }}</span></p>
                  <p>Size: {{ backupStatus.last_backup.size_mb.toFixed(2) }} MB</p>
                  <p>Duration: {{ backupStatus.last_backup.duration_seconds }}s</p>
                </div>
                <div class="next-backup">
                  <h4>Next Scheduled Backup</h4>
                  <p>{{ formatDate(backupStatus.next_scheduled_backup) }}</p>
                </div>
              </div>
            </div>
            
            <!-- Error Details -->
            <div class="card error-details">
              <h3>Error Analysis</h3>
              <div v-if="metrics.error_details.failed_requests === 0" class="no-errors">
                No errors recorded in the current session.
              </div>
              <div v-else>
                <p>Total Requests: {{ metrics.error_details.total_requests }} | Failed: {{ metrics.error_details.failed_requests }}</p>
                
                <h4>Errors by Type</h4>
                <div class="error-list">
                  <div v-for="(error, type) in metrics.error_details.errors_by_type" :key="type" class="error-item">
                    <div class="error-header">
                      <span class="error-type">{{ type }}</span>
                      <span class="error-count">{{ error.count }} occurrences</span>
                    </div>
                    <div class="error-endpoints">
                      <div v-for="(endpoint, path) in error.endpoints" :key="path" class="endpoint-item">
                        <div class="endpoint-path">{{ path }}: {{ endpoint.count }} errors</div>
                        <div v-if="endpoint.recent_errors && endpoint.recent_errors.length > 0" class="recent-error">
                          Most recent: {{ endpoint.recent_errors[endpoint.recent_errors.length - 1].message }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Accessibility Features -->
            <div class="card accessibility">
              <h3>Accessibility Features</h3>
              <div class="accessibility-controls">
                <div class="accessibility-option">
                  <label for="high-contrast">High Contrast</label>
                  <input type="checkbox" id="high-contrast" v-model="highContrast" @change="toggleHighContrast">
                </div>
                <div class="accessibility-option">
                  <label for="font-size">Font Size</label>
                  <select id="font-size" v-model="fontSize" @change="changeFontSize">
                    <option value="small">Small</option>
                    <option value="medium">Medium</option>
                    <option value="large">Large</option>
                  </select>
                </div>
                <div class="accessibility-option">
                  <label for="screen-reader">Screen Reader Support</label>
                  <input type="checkbox" id="screen-reader" v-model="screenReaderMode" @change="toggleScreenReaderMode">
                </div>
                <div class="accessibility-info">
                  <p>These accessibility features are designed to make the system more inclusive. Currently supporting:</p>
                  <ul>
                    <li>High contrast mode for better visibility</li>
                    <li>Font size adjustment for readability</li>
                    <li>Screen reader optimizations (aria attributes and semantic HTML)</li>
                    <li>Keyboard navigation (use Tab to navigate through interface)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import Chart from 'chart.js/auto';
  import sidebar from '@/components/admin/sidebar.vue';
  import Header from '@/components/Header.vue';
  import axios from 'axios';
  import { API_BASE_URL } from '@/api/config.js';
  
  export default {
    name: 'PerformanceMetrics',
    components: {
      sidebar,
      Header
    },
    data() {
      return {
        metrics: {
          current_metrics: {
        error_rate: 0,
        avg_transaction_time: 0,
        avg_stock_update_time: 0,
        avg_response_time: 0,
        concurrent_users: 0,
      },
      hourly_metrics: {},
      error_details: {
        total_requests: 0,
        failed_requests: 0,
        errors_by_type: {}
      },
      transaction_times: [],
  stock_update_times: []
    },
        dbStats: {
          connection_stats: {
            active_connections: 0,
            max_connections: 0,
            connection_usage_percent: 0
          },
          uptime: {
            seconds: 0,
            readable: "0:00:00"
          },
          table_stats: [],
          query_cache: {}
        },
        backupStatus: {
          last_backup: {
            timestamp: new Date(),
            status: "pending",
            size_mb: 0,
            duration_seconds: 0
          },
          next_scheduled_backup: new Date(),
          backup_history: []
        },
        isLoadingMetrics: true,
        isLoadingDbStats: true,
        isLoadingBackup: true,
        metricsError: null,
        dbStatsError: null,
        backupError: null,
        refreshInterval: null,
        responseTimeChart: null,
        
        // Accessibility settings
        highContrast: false,
        fontSize: 'medium',
        screenReaderMode: false
      }
    },
    computed: {
      hourlyLabels() {
        return Object.keys(this.metrics.hourly_metrics).map(key => {
          const date = new Date(key);
          return date.getHours() + ':00';
        });
      },
      hourlyResponseTimes() {
        return Object.values(this.metrics.hourly_metrics).map(metric => 
          metric.avg_response_time
        );
      }
    },
    async mounted() {
      await this.fetchAllMetrics();
      this.initResponseTimeChart();
      
      // Set up auto-refresh every 60 seconds
      this.refreshInterval = setInterval(() => {
        this.fetchAllMetrics();
      }, 60000);
      
      // Apply any saved accessibility settings
      this.loadAccessibilitySettings();
    },
    beforeUnmount() {
      // Clear the refresh interval when component is unmounted
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
      
      // Destroy chart instances to prevent memory leaks
      if (this.responseTimeChart) {
        this.responseTimeChart.destroy();
      }
    },
    methods: {
      getTransactionSpeedClass(time) {
      if (!time) return 'neutral';
      const speed = parseFloat(time);
      if (speed < 100) return 'positive';
      if (speed < 300) return 'positive';
      if (speed < 500) return 'neutral';
      return 'negative';
    },
    async fetchAllMetrics() {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/performance/metrics`);
    
    if (!response.data || !response.data.current_metrics) {
      throw new Error('Invalid metrics data structure');
    }

    this.metrics = {
      current_metrics: {
        error_rate: response.data.current_metrics.error_rate || 0,
        avg_transaction_time: response.data.current_metrics.avg_transaction_time || 0,
        avg_stock_update_time: response.data.current_metrics.avg_stock_update_time || 0,
        avg_response_time: response.data.current_metrics.avg_response_time || 0,
        concurrent_users: response.data.current_metrics.concurrent_users || 0,
      },
      hourly_metrics: response.data.hourly_metrics || {},
      error_details: response.data.error_details || {
        total_requests: 0,
        failed_requests: 0,
        errors_by_type: {}
      },
      transaction_times: response.data.transaction_times || [],
  stock_update_times: response.data.stock_update_times || []
    };

    if (this.responseTimeChart) {
      this.updateResponseTimeChart();
    }

  } catch (error) {
    console.error('Error fetching metrics:', error);
    this.metricsError = `Failed to load metrics data: ${error.message}`;
  }
},
      
      async fetchPerformanceMetrics() {
        try {
          this.isLoadingMetrics = true;
          const response = await axios.get(`${API_BASE_URL}/api/performance/metrics`);
          this.metrics = response.data;
          this.isLoadingMetrics = false;
          this.metricsError = null;
          
          // Update the chart if it exists
          if (this.responseTimeChart) {
            this.updateResponseTimeChart();
          }
        } catch (error) {
          console.error('Error fetching performance metrics:', error);
          this.metricsError = 'Failed to load metrics data. Please try again.';
          this.isLoadingMetrics = false;
        }
      },
      
      async fetchDatabaseStats() {
        try {
          this.isLoadingDbStats = true;
          const response = await axios.get(`${API_BASE_URL}/api/performance/database_stats`);
          this.dbStats = response.data;
          this.isLoadingDbStats = false;
          this.dbStatsError = null;
        } catch (error) {
          console.error('Error fetching database stats:', error);
          this.dbStatsError = 'Failed to load database statistics. Please try again.';
          this.isLoadingDbStats = false;
        }
      },
      
      async fetchBackupStatus() {
        try {
          this.isLoadingBackup = true;
          const response = await axios.get(`${API_BASE_URL}/api/performance/backup_status`);
          this.backupStatus = response.data;
          this.isLoadingBackup = false;
          this.backupError = null;
        } catch (error) {
          console.error('Error fetching backup status:', error);
          this.backupError = 'Failed to load backup information. Please try again.';
          this.isLoadingBackup = false;
        }
      },
      
      initResponseTimeChart() {
  if (!this.$refs.responseTimeChart) {
    console.warn('Chart canvas not found');
    return;
  }

    const ctx = this.$refs.responseTimeChart.getContext('2d');
    
    if (this.responseTimeChart) {
      this.responseTimeChart.destroy();
    }
    
    this.responseTimeChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: this.hourlyLabels || [],
        datasets: [{
          label: 'Response Time (ms)',
          data: this.hourlyResponseTimes || [],
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: 20
        },
        plugins: {
          legend: {
            display: true,
            position: 'top'
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Response Time (ms)'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Hour'
            }
          }
        }
      }
    });
  },

  updateResponseTimeChart() {
  if (!this.responseTimeChart) {
    this.initResponseTimeChart();
    return;
  }

    try {
      this.responseTimeChart.data.labels = this.hourlyLabels || [];
      this.responseTimeChart.data.datasets[0].data = this.hourlyResponseTimes || [];
      this.responseTimeChart.update('none'); // Use 'none' mode to prevent animation issues
    } catch (err) {
      console.error('Error updating chart:', err);
      // Reinitialize chart on error
      this.initResponseTimeChart();
    }
  },
      
      formatDate(dateString) {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }).format(date);
      },
      
      getTransactionSpeedStatus(time) {
    if (!time) return 'No data';
    const speed = parseFloat(time);
    if (speed < 100) return `Excellent (${speed.toFixed(2)}ms)`;
    if (speed < 300) return `Good (${speed.toFixed(2)}ms)`;
    if (speed < 500) return `Acceptable (${speed.toFixed(2)}ms)`;
    return `Needs improvement (${speed.toFixed(2)}ms)`;
  },

      getErrorRateStatus(rate) {
        if (rate === 0) return 'No errors';
        if (rate < 1) return 'Very low';
        if (rate < 5) return 'Moderate';
        return 'High - investigate';
      },
      
      getErrorStatusClass(rate) {
        if (rate === 0) return 'positive';
        if (rate < 1) return 'positive';
        if (rate < 5) return 'neutral';
        return 'negative';
      },
      
      getStockUpdateSpeedStatus(time) {
    if (!time) return 'No data';
    const speed = parseFloat(time);
    if (speed < 200) return `Fast (${speed.toFixed(2)}ms)`;
    if (speed < 500) return `Good (${speed.toFixed(2)}ms)`;
    if (speed < 1000) return `Acceptable (${speed.toFixed(2)}ms)`;
    return `Slow - optimize (${speed.toFixed(2)}ms)`;
  },

  getStockUpdateSpeedClass(time) {
    if (!time) return 'neutral';
    const speed = parseFloat(time);
    if (speed < 200) return 'positive';
    if (speed < 500) return 'positive';
    if (speed < 1000) return 'neutral';
    return 'negative';
  },

      
      // Accessibility methods
      toggleHighContrast() {
        document.body.classList.toggle('high-contrast', this.highContrast);
        this.saveAccessibilitySettings();
      },
      
      changeFontSize() {
        document.body.classList.remove('font-small', 'font-medium', 'font-large');
        document.body.classList.add(`font-${this.fontSize}`);
        this.saveAccessibilitySettings();
      },
      
      toggleScreenReaderMode() {
        document.body.classList.toggle('screen-reader-mode', this.screenReaderMode);
        this.saveAccessibilitySettings();
      },
      
      saveAccessibilitySettings() {
        const settings = {
          highContrast: this.highContrast,
          fontSize: this.fontSize,
          screenReaderMode: this.screenReaderMode
        };
        localStorage.setItem('accessibilitySettings', JSON.stringify(settings));
      },
      
      loadAccessibilitySettings() {
        try {
          const settings = JSON.parse(localStorage.getItem('accessibilitySettings'));
          if (settings) {
            this.highContrast = settings.highContrast;
            this.fontSize = settings.fontSize;
            this.screenReaderMode = settings.screenReaderMode;
            
            // Apply settings
            this.toggleHighContrast();
            this.changeFontSize();
            this.toggleScreenReaderMode();
          }
        } catch (error) {
          console.error('Error loading accessibility settings:', error);
        }
      },
      formatNumber(num) {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num;
  }
    }
  }
  </script>
  
  <style scoped>

.app-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  margin-left: 230px;
  min-height: 100vh;
}
  .dashboard-container {
    border-radius: 8px;
    padding: 20px;
  }
  
  .header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e9ecef;
}

.section-title {
  color: #333;
  font-size: 30px;
  font-family: 'Arial', sans-serif;
  font-weight: 900;
}
  
  .dashboard-grid {
    display: grid;
    gap: 20px;
  }
  
  .card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    position: relative;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
  
  .card h3 {
    font-size: 18px;
    margin-top: 0;
    margin-bottom: 15px;
    color: #333;
  }
  
  .card h4 {
    font-size: 16px;
    margin-top: 15px;
    margin-bottom: 10px;
    color: #555;
  }
  
  .stats {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }
  
  .stat-value {
    font-size: 28px;
    font-weight: bold;
    margin: 10px 0;
    color: #2c3e50;
  }
  
  .stat-change {
    font-size: 14px;
    padding: 4px 8px;
    border-radius: 30px;
    background-color: #f8f9fa;
  }
  
  .stat-change.positive {
    color: #28a745;
    background-color: rgba(40, 167, 69, 0.1);
  }
  
  .stat-change.negative {
    color: #dc3545;
    background-color: rgba(220, 53, 69, 0.1);
  }
  
  .stat-change.neutral {
    color: #fd7e14;
    background-color: rgba(253, 126, 20, 0.1);
  }
  
  .chart {
    grid-column: span 2;
  }
  
  .chart-container {
    height: 250px;
    position: relative;
  }
  
  .loading-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
    color: #6c757d;
  }
  
  .error-message {
    color: #dc3545;
    text-align: center;
    padding: 20px;
  }
  
  .db-stats, .backup-status, .error-details, .accessibility {
    grid-column: span 2;
  }
  
  .stat-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 15px;
  }
  
  .db-stat-item {
    flex: 1;
    min-width: 120px;
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 5px;
    text-align: center;
  }
  
  .db-stat-item .label {
    display: block;
    font-size: 14px;
    color: #6c757d;
    margin-bottom: 5px;
  }
  
  .db-stat-item .value {
    display: block;
    font-size: 16px;
    font-weight: bold;
    color: #495057;
  }
  
  .db-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }
  
  .db-table th, .db-table td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #dee2e6;
  }
  
  .db-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #495057;
  }
  
  .backup-info {
    display: flex;
    gap: 20px;
  }
  
  .last-backup, .next-backup {
    flex: 1;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 5px;
  }
  
  .backup-info p {
    margin: 5px 0;
  }
  
  .backup-info .success {
    color: #28a745;
    font-weight: bold;
  }
  
  .backup-info .failed {
    color: #dc3545;
    font-weight: bold;
  }
  
  .error-list {
    max-height: 250px;
    overflow-y: auto;
  }
  
  .error-item {
    margin-bottom: 15px;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 5px;
  }
  
  .error-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-weight: bold;
  }
  
  .error-type {
    color: #dc3545;
  }
  
  .error-count {
    color: #6c757d;
  }
  
  .endpoint-item {
    margin-left: 10px;
    margin-top: 5px;
    padding: 5px;
    border-left: 2px solid #dee2e6;
  }
  
  .endpoint-path {
    font-weight: 500;
    color: #495057;
  }
  
  .recent-error {
    font-size: 13px;
    color: #6c757d;
    margin-top: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
  }
  
  .no-errors {
    padding: 20px;
    text-align: center;
    color: #28a745;
  }
  
  /* Accessibility controls */
  .accessibility-controls {
    padding: 10px;
  }
  
  .accessibility-option {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .accessibility-option label {
    margin-right: 10px;
    flex: 0 0 150px;
  }
  
  .accessibility-info {
    margin-top: 15px;
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 5px;
  }
  
  .accessibility-info ul {
    padding-left: 20px;
  }
  
  /* High contrast mode */
  body.high-contrast {
    background-color: #000;
    color: #fff;
  }
  
  body.high-contrast .card {
    background-color: #333;
    color: #fff;
    border: 1px solid #666;
  }
  
  body.high-contrast .card h3,
  body.high-contrast .card h4,
  body.high-contrast .stat-value {
    color: #fff;
  }
  
  /* Font size adjustments */
  body.font-small {
    font-size: 14px;
  }
  
  body.font-medium {
    font-size: 16px;
  }
  
  body.font-large {
    font-size: 18px;
  }
  
  /* Screen reader mode */
  body.screen-reader-mode:focus-within {
    outline: 3px solid #2196f3;
  }
  
  /* Responsive adjustments */
  @media (max-width: 1200px) {
    .dashboard-grid {
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    }
  }
  
  @media (max-width: 768px) {
    .app-container {
      margin-left: 0;
      padding: 10px;
    }
    
    .dashboard-grid {
      grid-template-columns: 1fr;
    }
    
    .chart, .db-stats, .backup-status, .error-details, .accessibility {
      grid-column: span 1;
    }
    
    .backup-info {
      flex-direction: column;
    }
  }
  </style> 