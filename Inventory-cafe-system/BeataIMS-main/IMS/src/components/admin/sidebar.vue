<template>
    <div :class="['sidebar', { 'collapsed': isCollapsed }]">
      <ul v-if="!isCollapsed" class="sidebar-list">
        <li v-for="(link, index) in links" :key="index">
          <router-link
            v-if="link.submenu"
            :to="link.path"
            class="sidebar-link"
            @click.prevent="toggleSubmenu(link)"  
          >
            <i :class="['pi', link.icon]"></i> {{ link.name }}
          </router-link>
          <router-link
            v-else
            :to="link.path"
            class="sidebar-link"
            active-class="active-link"
          >
            <i :class="['pi', link.icon]"></i> {{ link.name }}
          </router-link>
  
          <!-- Submenu that stays open when toggled -->
          <ul v-if="link.submenu && link.isOpen" class="submenu">
            <li v-for="(subLink, subIndex) in link.submenu" :key="subIndex">
              <router-link
                :to="subLink.path"
                class="sidebar-link"
                active-class="active-link"
                @click.stop="stayOpen" 
              >
                <i :class="['pi', subLink.icon]"></i> {{ subLink.name }}
              </router-link>
            </li>
          </ul>
        </li>
      </ul>
  
      <ul v-else class="sidebar-list">
        <li v-for="(link, index) in links" :key="index">
          <router-link :to="link.path" class="sidebar-link" active-class="active-link">
            <i :class="['pi', link.icon]"></i>
          </router-link>
        </li>
      </ul>
  
      <!-- Logout at the bottom with margin -->
      
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        isCollapsed: false,
        links: [
          { name: 'Home', path: 'dashboard', icon: 'pi-home' },
          { name: 'Users', path: '/users', icon: 'pi-user' },
          { name: 'Forecasting', path: '/forecasting', icon: 'pi-chart-line' }
        ]
      };
    },
    mounted() {
      this.checkActiveSubmenu();
    },
    methods: {
      toggleSubmenu(link) {
        if (link.submenu) {
          link.isOpen = !link.isOpen; 
        }
      },
      stayOpen() {
        // Prevent submenu from closing when a submenu item is clicked
      },
      checkActiveSubmenu() {
        this.links.forEach(link => {
          if (link.submenu) {
            link.isOpen = link.submenu.some(subLink => this.$route.path === subLink.path);
          }
        });
      },
      logout() {
        console.log("Logging out...");
      }
    }
  };
  </script>
  
  <style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 180px;
  padding: 20px;
  background-color: rgb(255, 255, 255);
  height: 100vh;
  box-shadow: 0 8px 8px rgba(0, 0, 0, 0.1);
  position: fixed;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 70px;
  padding: 20px 5px;
}

.sidebar-list {
  list-style-type: none;
  padding: 0;
  margin-bottom: auto;
}

.sidebar-link {
  color: rgba(14, 14, 14, 0.54);
  text-decoration: none;
  font-weight: 450;
  font-size: 15px;
  display: flex;
  align-items: center;
  padding: 10px 10px;
  margin: 10px 0;
  border-radius: 10px;
  transition: all 0.3s ease;
  gap: 10px; /* Add gap between icon and text */
}

.sidebar.collapsed .sidebar-link {
  justify-content: center;
  padding: 12px;
}

.sidebar.collapsed .sidebar-link span {
  display: none;
}

.sidebar-link i {
  font-size: 18px;
  min-width: 24px;
  text-align: center;
}

.sidebar-link:hover {
  color: #000000;
  background-color: #f0f0f0;
}

.active-link {
  color: #000000;
  font-weight: bold;
  background-color: #ed9598 !important;
  padding: 8px 5px !important;
  width: 100%;
  box-sizing: content-box;
  border-radius: 10px;
}

.submenu {
  list-style-type: none;
  padding-left: 20px;
  margin: 10px 0;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 20px;
}

.sidebar-footer .sidebar-link {
  justify-content: center;
}

.sidebar-footer .sidebar-link span {
  display: none;
}

.sidebar-footer .sidebar-link i {
  font-size: 18px;
}

.sidebar.collapsed .sidebar-footer .sidebar-link {
  justify-content: center;
}

@media (max-width: 768px) {
  .sidebar {
    width: 70px;
    padding: 20px 5px;
  }

  .sidebar-link span {
    display: none;
  }

  .sidebar-link {
    justify-content: center;
  }

  .submenu {
    display: none;
  }
}
</style>