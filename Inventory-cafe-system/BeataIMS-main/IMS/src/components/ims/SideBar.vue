<template>
  <div :class="['sidebar', { 'collapsed': isCollapsed }]">
    <ul class="sidebar-list">
      <li v-for="(link, index) in links" :key="index">
        <!-- Main menu items -->
        <router-link
          :to="link.submenu ? '#' : link.path"
          class="sidebar-link"
          :class="{ 'has-submenu': link.submenu }"
          @click.prevent="link.submenu ? toggleSubmenu(link) : null"
        >
          <i :class="['pi', link.icon]"></i>
          <span v-if="!isCollapsed">{{ link.name }}</span>
        </router-link>

        <!-- Submenu items -->
        <transition name="submenu">
          <ul v-if="!isCollapsed && link.submenu && link.isOpen" class="submenu">
            <li v-for="(subLink, subIndex) in link.submenu" :key="subIndex">
              <router-link
                :to="subLink.path"
                class="sidebar-link"
                active-class="active-link"
              >
                <i :class="['pi', subLink.icon]"></i>
                <span>{{ subLink.name }}</span>
              </router-link>
            </li>
          </ul>
        </transition>
      </li>
    </ul>

  </div>
</template>

<script>
export default {
  name: "SideBar",
  props: {
    isCollapsed: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      links: [
        { name: "Home", path: "/homeims", icon: "pi-home" },
        {
          name: "Product",
          path: "#",
          icon: "pi-box",
          submenu: [
            { name: "Create Product", path: "/create", icon: "pi-plus-circle" },
            { name: "View Products", path: "/products", icon: "pi-eye" },
            { name: "View Sales Product", path: "/productsales", icon: "pi-eye" },
          ],
          isOpen: false,
        },
        {
          name: "Sales",
          path: "#",
          icon: "pi pi-dollar",
          submenu: [
            { name: "Create Orders", path: "/createorder", icon: "pi-plus-circle" },
            { name: "View Sales", path: "/ordershistory", icon: "pi-eye" },
          ],
          isOpen: false,
        },
        {
          name: "Inventory",
          path: "#",
          icon: "pi-warehouse",
          submenu: [
            { name: "View Inventory", path: "/viewinventory", icon: "pi-eye" },
            { name: "Stock-in", path: "/stocks", icon: "pi-plus-circle" },
          ],
          isOpen: false,
        },
        { name: "Suppliers", path: "/suppliers", icon: "pi-truck" },
        { name: "Categories", path: "/category", icon: "pi-list" },
        { name: "Reports", path: "/reportsims", icon: "pi-chart-line" },
      ],
    };
  },
  methods: {
    toggleSubmenu(link) {
      if (link.submenu) {
        link.isOpen = !link.isOpen;
      }
    },

  },
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