<template>
    <div class="stat-card">
      <i :class="['fas', icon, 'stat-icon']"></i>
      <div class="stat-info">
        <h3>{{ title }}</h3>
        <p class="stat-value">{{ value }}</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'StatCard',
    props: {
      title: {
        type: String,
        required: true
      },
      value: {
        type: [String, Number],
        required: true
      },
      icon: {
        type: String,
        required: true
      }
    }
  }
  </script>
  
  <style scoped>
  .stat-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 15px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .stat-icon {
    font-size: 24px;
    color: #FF32BA;
  }
  
  .stat-info h3 {
    margin: 0;
    font-size: 14px;
    color: #666;
  }
  
  .stat-value {
    margin: 5px 0 0;
    font-size: 24px;
    font-weight: bold;
    color: #000;
  }
  </style>
  