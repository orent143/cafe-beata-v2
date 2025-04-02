<template>
  <div class="coffee-container">
    <header class="header">
      <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
      <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
      <div class="logo" @click="showMainContent">
        <img src="@/assets/cafe-logo.png" alt="Cafe Logo" class="cafe-logo" />
      </div>
      <nav class="nav-links">
        <a href="javascript:void(0);" @click="showMainContent">Home</a>
        <a href="javascript:void(0);" @click="showContactContent">Contact Us</a>       
        <a href="javascript:void(0);" @click="showAboutContent">About Us</a>
        <a href="javascript:void(0);" @click="goToPage('/create-account')">Sign up</a>
      </nav>
    </header>

    <!-- Main Content -->
    <div v-if="currentView === 'main'">
      <section class="hero" id="home">
        <div class="hero-text">
          <h1>Enjoy Your Morning Coffee in UIC Café Beàta</h1>
          <p>Boost your productivity and build your mood with a glass of coffee in the morning.</p>
          <button class="get-now-btn" @click="goToPage('/login')">Get your Coffee now!</button>
          <button class="play-video-btn" @click="toggleVideo">Watch Video</button>
        </div>
        <div class="hero-image">
          <img :src="require('@/assets/pink-cafe.png')" alt="Coffee Cup" />
        </div>
      </section>

      <!-- Video Modal -->
      <div v-if="showVideo" class="video-modal" @click="toggleVideo">
        <div class="video-container" @click.stop>
          <video ref="videoPlayer" controls>
            <source :src="require('@/assets/Uic Cafe Video.mp4')" type="video/mp4">
            Your browser does not support the video tag.
          </video>
          <button class="close-video" @click="toggleVideo">&times;</button>
        </div>
      </div>

      <!-- Best Selling Item Section -->
      <section class="best-selling" id="best-selling">
        <h2>Best Selling Item</h2>
        <p class="description">UIC Café Beata – Since 2020 Our top-selling item stands out for its exceptional quality and taste. Crafted with the finest ingredients, it has been a customer favorite since we first opened our doors. Experience the perfect blend of flavor and tradition with every bite.</p>
        
        <div class="filter-menu">
          <span 
            v-for="category in ['All', 'Americano', 'Espresso', 'Latte']" 
            :key="category"
            :class="{ active: selectedCategory === category }"
            @click="filterByCategory(category)"
          >
            {{ category }}
          </span>
        </div>

        <div class="coffee-items">
          <div v-for="item in displayedItems" :key="item.name" class="coffee-card">
            <div class="coffee-img-container">
              <img :src="require(`@/assets/${item.image}`)" :alt="item.name" />
            </div>
            <h3>{{ item.name }}</h3>
            <p class="category">{{ item.category }}</p>
            <button class="order-now-btn" @click="goToPage('/login')">Order Now</button>
          </div>
        </div>

        <div class="pagination">
          <button class="prev-btn" @click="prevItem">
            <i class="fas fa-chevron-left"></i>
          </button>
          
          <div class="pagination-indicators">
            <span 
              v-for="(_, index) in filteredItems" 
              :key="index" 
              :class="{ active: index === currentIndex }"
              @click="currentIndex = index"
            ></span>
          </div>
          
          <button class="next-btn" @click="nextItem">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </section>

      <!-- Footer Section -->
      <footer>
        <div class="footer-content">
          <div class="footer-section">
            <h3>UIC Café Beàta</h3>
            <p>Making your coffee experience delightful, one cup at a time.</p>
          </div>
          <div class="footer-section">
            <h3>Quick Links</h3>
            <ul>
              <li><a href="javascript:void(0);" @click="showMainContent">Home</a></li>
              <li><a href="javascript:void(0);" @click="scrollToSection('best-selling')">Menu</a></li>
              <li><a href="javascript:void(0);" @click="showAboutContent">About Us</a></li>
              <li><a href="javascript:void(0);" @click="showContactContent">Contact</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h3>Contact Us</h3>
            <p><i class="fas fa-map-marker-alt"></i> Fr Selga, Davao City, Philippines</p>
            <p><i class="fas fa-phone"></i> (321) 562 – 57420</p>
            <p><i class="fas fa-envelope"></i> cafebeata2020@gmail.com</p>
          </div>
          <div class="footer-section">
            <h3>Follow Us</h3>
            <div class="social-icons">
              <a href="https://www.facebook.com/profile.php?id=61573775720122" target="_blank">
                <i class="fab fa-facebook"></i>
              </a>
              <a href="https://www.instagram.com/uic_ph/" target="_blank">
                <i class="fab fa-instagram"></i>
              </a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2025 UIC Café Beàta. All rights reserved.</p>
        </div>
      </footer>
    </div>

    <!-- About Content -->
    <div v-if="currentView === 'about'" class="about-page">
      <div class="about-container">
        <div class="about-header">
          <h2>Our Story</h2>
          <p>Discover the passion behind UIC Café Beàta</p>
        </div>
        
        <div class="about-story">
          <div class="about-image">
            <img :src="require('@/assets/cafe-beatas.png')" alt="Cafe Interior">
          </div>
          <div class="about-text">
            <h3>How It All Began</h3>
            <p>UIC Café Beàta was founded in 2020 as a welcoming space for students, faculty, and staff at the University of the Immaculate Conception. What started as a small campus café has grown into a beloved community gathering place.</p>
            <p>Our mission has always been simple: serve exceptional coffee in a warm, welcoming environment while building meaningful connections with our campus community.</p>
            <p>Over the years, we've expanded our menu to include a variety of specialty coffees, teas, and freshly baked goods, but our commitment to quality and service remains unchanged.</p>
            <p>In 2025, we launched our pre-order system to make your coffee experience even more convenient, allowing you to skip the line and pick up your favorite items at your convenience.</p>
          </div>
        </div>
        
        <div class="about-values">
          <h3>Our Values</h3>
          <div class="values-container">
            <div class="value-card">
              <i class="fas fa-coffee"></i>
              <h4>Quality</h4>
              <p>We source only the finest beans and ingredients, ensuring every cup and bite exceeds expectations.</p>
            </div>
            <div class="value-card">
              <i class="fas fa-handshake"></i>
              <h4>Community</h4>
              <p>We believe in building strong relationships with our customers, suppliers, and campus community.</p>
            </div>
            <div class="value-card">
              <i class="fas fa-leaf"></i>
              <h4>Sustainability</h4>
              <p>We're committed to environmentally responsible practices in all aspects of our business.</p>
            </div>
            <div class="value-card">
              <i class="fas fa-heart"></i>
              <h4>Passion</h4>
              <p>Our love for coffee drives us to continuously improve and innovate our offerings.</p>
            </div>
          </div>
        </div>
        
        <!-- Team Section -->
        <div class="team-section">
          <h3>Meet Our Team</h3>
          <div class="team-grid">
            <div class="team-member">
              <img :src="require('@/assets/sanji.png')" alt="Team Member 1">
              <h4>Leynard Librando</h4>
              <p class="role">Programmer</p>
              <p class="description">Leading our team with passion and dedication.</p>
            </div>
            <div class="team-member">
              <img :src="require('@/assets/luffy.png')" alt="Team Member 2">
              <h4>Marc Laurence Lapating</h4>
              <p class="role">Analyst</p>
              <p class="description">Bringing technical expertise and innovation.</p>
            </div>
            <div class="team-member">
              <img :src="require('@/assets/zoroo.png')" alt="Team Member 3">
              <h4>Gi Linghon</h4>
              <p class="role">Project Manager</p>
              <p class="description">Creating beautiful and intuitive experiences.</p>
            </div>
          </div>
        </div>
      </div>
      <!-- Footer Section -->
      <footer>
        <div class="footer-content">
          <div class="footer-section">
            <h3>UIC Café Beàta</h3>
            <p>Making your coffee experience delightful, one cup at a time.</p>
          </div>
          <div class="footer-section">
            <h3>Quick Links</h3>
            <ul>
              <li><a href="javascript:void(0);" @click="showMainContent">Home</a></li>
              <li><a href="javascript:void(0);" @click="scrollToSection('best-selling')">Menu</a></li>
              <li><a href="javascript:void(0);" @click="showAboutContent">About Us</a></li>
              <li><a href="javascript:void(0);" @click="showContactContent">Contact</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h3>Contact Us</h3>
            <p><i class="fas fa-map-marker-alt"></i> Fr Selga, Davao City, Philippines</p>
            <p><i class="fas fa-phone"></i> (321) 562 – 57420</p>
            <p><i class="fas fa-envelope"></i> cafebeata2020@gmail.com</p>
          </div>
          <div class="footer-section">
            <h3>Follow Us</h3>
            <div class="social-icons">
              <a href="https://www.facebook.com/profile.php?id=61573775720122" target="_blank">
                <i class="fab fa-facebook"></i>
              </a>
              <a href="https://www.instagram.com/uic_ph/" target="_blank">
                <i class="fab fa-instagram"></i>
              </a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2025 UIC Café Beàta. All rights reserved.</p>
        </div>
      </footer>
    </div>

    <!-- Contact Content -->
    <div v-if="currentView === 'contact'" class="contact-page">
      <div class="contact-container">
        <div class="contact-header">
          <h2>Contact Us</h2>
          <p>We'd love to hear from you! Reach out with any questions or feedback.</p>
        </div>
        
        <div class="contact-content">
          <div class="contact-info-card">
            <div class="icon-circle">
              <i class="fas fa-map-marker-alt"></i>
            </div>
            <h3>Visit Us</h3>
            <p>Fr Selga, Davao City</p>
            <p>Philippines</p>
          </div>
          
          <div class="contact-info-card">
            <div class="icon-circle">
              <i class="fas fa-phone-alt"></i>
            </div>
            <h3>Call Us</h3>
            <p>(321) 562 – 57420</p>
            <p>Mon-Fri: 7am - 7pm</p>
          </div>
          
          <div class="contact-info-card">
            <div class="icon-circle">
              <i class="fas fa-envelope"></i>
            </div>
            <h3>Email Us</h3>
            <p>cafebeata2020@gmail.com</p>
            <p>We'll respond within 24 hours</p>
          </div>

          <div class="contact-info-card">
            <div class="icon-circle">
              <i class="fas fa-clock"></i>
            </div>
            <h3>Opening Hours</h3>
            <p>Monday - Saturday: 6am - 9pm</p>
            <p>Weekends: Closed</p>
          </div>
          
          <div class="contact-form-container">
            <h3>Send Us a Message</h3>
            <form @submit.prevent="handleContactSubmit" class="contact-form">
              <div class="form-group">
                <label for="name">Your Name</label>
                <input type="text" id="name" v-model="contactForm.name" required>
              </div>
              
              <div class="form-group">
                <label for="email">Your Email</label>
                <input type="email" id="email" v-model="contactForm.email" required>
              </div>
              
              <div class="form-group">
                <label for="subject">Subject</label>
                <input type="text" id="subject" v-model="contactForm.subject" required>
              </div>
              
              <div class="form-group">
                <label for="message">Message</label>
                <textarea id="message" v-model="contactForm.message" rows="5" required></textarea>
              </div>
              
              <button type="submit" class="btn btn-primary">Send Message</button>
            </form>
          </div>
        </div>
      </div>
      <!-- Footer Section -->
      <footer>
        <div class="footer-content">
          <div class="footer-section">
            <h3>UIC Café Beàta</h3>
            <p>Making your coffee experience delightful, one cup at a time.</p>
          </div>
          <div class="footer-section">
            <h3>Quick Links</h3>
            <ul>
              <li><a href="javascript:void(0);" @click="showMainContent">Home</a></li>
              <li><a href="javascript:void(0);" @click="scrollToSection('best-selling')">Menu</a></li>
              <li><a href="javascript:void(0);" @click="showAboutContent">About Us</a></li>
              <li><a href="javascript:void(0);" @click="showContactContent">Contact</a></li>
            </ul>
          </div>
          <div class="footer-section">
            <h3>Contact Us</h3>
            <p><i class="fas fa-map-marker-alt"></i> Fr Selga, Davao City, Philippines</p>
            <p><i class="fas fa-phone"></i> (321) 562 – 57420</p>
            <p><i class="fas fa-envelope"></i> cafebeata2020@gmail.com</p>
          </div>
          <div class="footer-section">
            <h3>Follow Us</h3>
            <div class="social-icons">
              <a href="https://www.facebook.com/profile.php?id=61573775720122" target="_blank">
                <i class="fab fa-facebook"></i>
              </a>
              <a href="https://www.instagram.com/uic_ph/" target="_blank">
                <i class="fab fa-instagram"></i>
              </a>
            </div>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2025 UIC Café Beàta. All rights reserved.</p>
        </div>
      </footer>
    </div>
  </div>

  <!-- Notification Component -->
  <transition name="fade">
    <div v-if="showNotification" :class="['notification', notificationType]">
      {{ notificationMessage }}
    </div>
  </transition>
</template>

<script>
export default {
  data() {
    return {
      currentView: 'main',
      items: [
        { name: 'Cappuccino', image: 'cappuccino.png', category: 'Latte' },
        { name: 'Americano', image: 'americano.png', category: 'Americano' },
        { name: 'Espresso', image: 'espresso.png', category: 'Espresso' },
        { name: 'Latte', image: 'latte.png', category: 'Latte' },
        { name: 'Mocha', image: 'mochaa.png', category: 'Latte' }
      ],
      currentIndex: 0,
      selectedCategory: 'All',
      email: '',
      showNotification: false,
      notificationMessage: '',
      notificationType: 'success',
      showVideo: false,
      contactForm: {
        name: '',
        email: '',
        subject: '',
        message: ''
      },
      windowWidth: window.innerWidth
    };
  },
  computed: {
    filteredItems() {
      if (this.selectedCategory === 'All') {
        return this.items;
      }
      return this.items.filter(item => item.category === this.selectedCategory);
    },
    displayedItems() {
      // For mobile view (less than 768px), show only 1 item
      if (this.isMobileView) {
        return this.filteredItems.slice(this.currentIndex, this.currentIndex + 1);
      }
      // For desktop view, show 3 items
      return this.filteredItems.slice(this.currentIndex, this.currentIndex + 3);
    },
    isMobileView() {
      return this.windowWidth <= 768;
    }
  },
  mounted() {
    // Add event listener for window resize
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    // Remove event listener when component is destroyed
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    handleResize() {
      // Update window width
      this.windowWidth = window.innerWidth;
      // Force re-evaluation of computed properties
      this.$forceUpdate();
    },
    showMainContent() {
      this.currentView = 'main';
      this.scrollToTop();
    },
    showAboutContent() {
      this.currentView = 'about';
      this.scrollToTop();
    },
    showContactContent() {
      this.currentView = 'contact';
      this.scrollToTop();
    },
    prevItem() {
      const itemsPerPage = this.isMobileView ? 1 : 3;
      if (this.currentIndex > 0) {
        this.currentIndex--;
      } else {
        // Go to the last possible index
        this.currentIndex = Math.max(0, this.filteredItems.length - itemsPerPage);
      }
    },
    nextItem() {
      const itemsPerPage = this.isMobileView ? 1 : 3;
      if (this.currentIndex < this.filteredItems.length - itemsPerPage) {
        this.currentIndex++;
      } else {
        // Go back to the beginning
        this.currentIndex = 0;
      }
    },
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },
    scrollToSection(sectionId) {
      const section = document.getElementById(sectionId);
      if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
      }
    },
    goToPage(pageUrl) {
      this.$router.push(pageUrl);
    },
    filterByCategory(category) {
      this.selectedCategory = category;
      this.currentIndex = 0;
    },
    toggleVideo() {
      this.showVideo = !this.showVideo;
      if (this.showVideo) {
        // Wait for the video element to be mounted
        this.$nextTick(() => {
          if (this.$refs.videoPlayer) {
            this.$refs.videoPlayer.play();
          }
        });
      } else {
        if (this.$refs.videoPlayer) {
          this.$refs.videoPlayer.pause();
        }
      }
    },
    handleContactSubmit() {
      // Store message in localStorage
      const messages = JSON.parse(localStorage.getItem('contactMessages')) || [];
      messages.push({
        ...this.contactForm,
        date: new Date().toISOString()
      });
      localStorage.setItem('contactMessages', JSON.stringify(messages));
      
      // Show success notification
      this.showNotification = true;
      this.notificationMessage = 'Your message has been sent successfully! We\'ll get back to you soon.';
      this.notificationType = 'success';
      
      // Reset form
      this.contactForm = {
        name: '',
        email: '',
        subject: '',
        message: ''
      };
      
      // Hide notification after 3 seconds
      setTimeout(() => {
        this.showNotification = false;
      }, 3000);
    }
  }
};
</script>

<style scoped>
/* Mobile Responsive Adjustments */
@media (max-width: 768px) {
  .best-selling {
    padding: 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    box-sizing: border-box;
  }

  .best-selling h2 {
    font-size: 2em;
  }

  .description {
    font-size: 1em;
    max-width: 100%;
    padding: 0 10px;
  }

  .filter-menu {
    flex-wrap: wrap;
    gap: 10px;
    font-size: 1em;
  }

  .coffee-items {
    flex-direction: column;
    align-items: center;
    width: 100%;
    position: relative;
    display: flex;
    justify-content: center;
    padding: 0;
  }

  .coffee-card {
    max-width: 280px;
    width: 100%;
    padding: 0;
    margin: 0 auto;
    border-width: 3px;
    overflow: hidden;
  }

  .coffee-img-container {
    height: 250px;
    width: 100%;
    background-color: #332621;
    border-radius: 8px 8px 0 0;
    overflow: hidden;
    padding: 0;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .coffee-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    margin: 0;
  }
  
  .coffee-card h3 {
    font-size: 1.5em;
    margin-top: 15px;
    padding: 0 15px;
  }
  
  .coffee-card p.category {
    padding: 0 15px;
  }

  .coffee-card button {
    font-size: 1.1em;
    padding: 12px;
    margin: 15px;
    width: calc(100% - 30px);
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 280px;
    margin-left: auto;
    margin-right: auto;
    gap: 10px;
    padding: 0;
    box-sizing: border-box;
  }

  .pagination-indicators {
    display: flex;
    gap: 8px;
    flex: 1;
    justify-content: center;
    margin: 0 5px;
  }

  .pagination button {
    font-size: 1.2em;
    padding: 10px;
    width: 45px;
    height: 45px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin: 0;
    background-color: #3b2a2a;
  }
}

@media (max-width: 480px) {
  .best-selling {
    padding: 20px;
  }

  .filter-menu {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
  }

  .coffee-card {
    max-width: 260px;
    width: 100%;
    padding: 0;
    border-width: 2px;
  }

  .coffee-img-container {
    height: 220px;
    padding: 0;
  }

  .coffee-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
  }
  
  .coffee-card h3 {
    font-size: 1.3em;
    padding: 0 10px;
    margin-top: 10px;
  }
  
  .coffee-card p.category {
    padding: 0 10px;
  }

  .coffee-card button {
    font-size: 1em;
    padding: 10px;
    margin: 10px;
    width: calc(100% - 20px);
  }

  .pagination {
    width: 260px;
    gap: 5px;
  }

  .pagination-indicators {
    gap: 6px;
  }

  .pagination button {
    font-size: 1.1em;
    width: 40px;
    height: 40px;
    padding: 8px;
  }
}

/* Best Selling Section */
.best-selling {
  background-color:rgb(233, 177, 177);
  padding: 50px;
  text-align: center;
  border-radius: 15px;
  margin: 40px auto;
  max-width: 1000px;
  border: 1px solid black;
}

.best-selling h2 {
  font-size: 2.5em;
  color: #3b2a2a;
}

.filter-menu {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 1.2em;
  font-weight: bold;
  margin-bottom: 30px;
}

.filter-menu span {
  cursor: pointer;
  padding: 5px 10px;
}

.filter-menu .active {
  text-decoration: underline;
}

.coffee-items {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
  width: 100%;
  margin: 0 auto;
 
}

.coffee-card {
  background-color: #332621;
  padding: 0;
  border-radius: 10px;
  text-align: center;
  width: 300px;
  flex: 0 0 auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  border: 4px solid black;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
  margin: 0;
}

.coffee-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
}

.coffee-img-container {
  background-color: #332621;
  padding: 0;
  border-radius: 0;
  margin-bottom: 0;
  height: 200px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.coffee-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  border-radius: 0;
  transition: transform 0.3s ease;
  position: absolute;
  top: 0;
  left: 0;
}

.coffee-card:hover img {
  transform: scale(1.05);
}

.coffee-card h3 {
  font-size: 1.5em;
  color: white;
  font-weight: bold;
  margin-top: 15px;
  padding: 0 15px;
}

.coffee-card p.category {
  color: #d4a76a;
  font-size: 0.9em;
  margin-bottom: 10px;
  padding: 0 15px;
}

.coffee-card button {
  background-color: #d2a679;
  color: black;
  border: none;
  padding: 10px;
  font-size: 1em;
  cursor: pointer;
  margin: 10px 15px 15px;
  border-radius: 5px;
  width: calc(100% - 30px);
  font-weight: bold;
}

.coffee-card button:hover {
  background-color: #b4845c;
}

.pagination {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  width: 100%;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.pagination-indicators {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
  margin: 0 10px;
}

.pagination-indicators span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #d2a679;
  opacity: 0.5;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-indicators span.active {
  opacity: 1;
  transform: scale(1.2);
  background-color: #3b2a2a;
}

.pagination button {
  background: #3b2a2a;
  color: white;
  border: 1px solid #2a1f1f;
  padding: 10px 20px;
  font-size: 1.2em;
  cursor: pointer;
  margin: 5px;
  border-radius: 5px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.pagination button:hover {
  background: #2a1f1f;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.pagination button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.prev-btn, .next-btn {
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50% !important;
  padding: 0 !important;
}

.prev-btn i, .next-btn i {
  font-size: 1.2em;
  transition: transform 0.3s ease;
}

.prev-btn:hover i {
  transform: translateX(-2px);
}

.next-btn:hover i {
  transform: translateX(2px);
}

.coffee-container {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-image: linear-gradient(to right, #E54F70, #ed9598);
  z-index: 1000;
  position: sticky;
  top: 0;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  animation: slideIn 0.5s ease-out;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.8em;
  font-weight: bold;
  font-family: 'Roboto', sans-serif;
  color: white;
  margin-left: 10px;
  cursor: pointer;
  text-transform: uppercase;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.1);
}

.nav-links {
  display: flex;
  gap: 20px;
  font-size: 1.1em;
  font-weight: bold;
  font-family: 'Roboto', sans-serif;
  color: #ffffff;
}

.nav-links a {
  text-decoration: none;
  color: #ffffff;
  transition: color 0.3s ease, transform 0.3s ease;
  cursor: pointer;
}

.nav-links a:hover {
  color: rgba(255, 255, 255, 0.8);
  transform: translateY(-3px);
  text-decoration: none;
}

.hero {
  display: flex;
  justify-content: space-between;
  padding: 40px;
  background: white;
  flex-wrap: wrap;
  animation: fadeIn 1s ease-in-out;
}

.hero-text {
  max-width: 50%;
  padding: 20px;
  animation: slideInRight 1s ease-out;
}

.hero-text h1 {
  font-size: 3em;
  color: #3b2a2a;
  animation: fadeIn 1s ease-in-out;
}

.hero-text p {
  margin-top: 10px;
  font-size: 1.2em;
  color: #5e5e5e;
  animation: fadeIn 1s ease-in-out 0.5s;
}

.get-now-btn,
.play-video-btn {
  background-color: #f4a261;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 1em;
  cursor: pointer;
  margin-top: 20px;
  margin-right: 10px;
  border-radius: 5px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.get-now-btn:hover,
.play-video-btn:hover {
  background-color: #e0763d;
  transform: scale(1.05);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.hero-image {
  max-width: 50%;
}

.hero-image img {
  max-width: 100%;
  height: auto;
  border-radius: 10px;
  animation: fadeIn 1s ease-in-out 0.8s;
  transition: transform 0.3s ease;
}

.hero-image img:hover {
  transform: scale(1.05);
}

/* About Us Section */
.about-us {
  background-color: white;
  padding: 40px;
  text-align: center;
  animation: fadeIn 1s ease-in-out 1s;
  border-radius: 15px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.about-us h2 {
  font-size: 2.5em;
  color: #3b2a2a;
}

.about-us p {
  font-size: 1em;
  color: #5e5e5e;
  max-width: 800px;
  margin: 0 auto;
}

/* Contact Us Section */
.contact-us {
  background-color: white;
  color: #333;
  padding: 50px 20px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 15px;
  margin: 20px;
}

.contact-header h2 {
  font-size: 2.5em;
  font-weight: bold;
}

.contact-header p {
  font-size: 1em;
  margin-bottom: 20px;
}

.newsletter {
  display: flex;
  justify-content: center;
  margin-top: 10px;
}

.newsletter input {
  width: 300px;
  padding: 10px;
  font-size: 1em;
  border: none;
  outline: none;
}

.newsletter button {
  background: #3b2a2a;
  color: white;
  border: 1px solid #2a1f1f;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 1.2em;
  border-radius: 5px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.newsletter button:hover {
  background: #2a1f1f;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.contact-content {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  margin: 0 auto;
  max-width: 1200px;
}

.contact-box {
  background-color: #f8d1d1;
  padding: 3px;
  border-radius: 10px;
  width: 300px;
  text-align: center;
  margin-bottom: 20px;
}

.contact-title {
  font-size: 1.5em;
  font-weight: bold;
  color: black;
}

.contact-box p {
  font-size: 1em;
  margin: 10px 0;
}

.social-icons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.social-icons a img {
  width: 30px;
  height: 30px;
  transition: transform 0.3s ease;
}

.social-icons a img:hover {
  transform: scale(1.1);
}

.copyright {
  margin-top: 30px;
  font-size: 0.9em;
  opacity: 0.8;
}

/* Responsive Design */
@media (max-width: 768px) {
  .contact-header h2 {
    font-size: 2em;
  }

  .contact-content {
    flex-direction: column;
    align-items: center;
  }

  .contact-box {
    width: 80%;
  }

  .newsletter input {
    width: 250px;
  }
}

@media (max-width: 480px) {
  .contact-header h2 {
    font-size: 1.8em;
  }

  .newsletter input {
    width: 200px;
  }

  .contact-box {
    width: 100%;
  }

  .social-icons a img {
    width: 25px;
    height: 25px;
  }
}

.about-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #fce6e6;
  min-height: calc(100vh - 80px); /* Adjust based on your header height */
}

.about-container {
  background-color: #fff;
  border-radius: 10px;
  padding: 2rem;
}

.about-header {
  text-align: center;
  margin-bottom: 3rem;
}

.about-header h2 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.about-story {
  display: flex;
  gap: 2rem;
  margin-bottom: 3rem;
}

.about-image {
  flex: 1;
}

.about-image img {
  width: 100%;
  border-radius: 10px;
  object-fit: cover;
}

.about-text {
  flex: 1;
}

.about-text h3 {
  color: #333;
  margin-bottom: 1rem;
}

.about-values {
  margin-bottom: 3rem;
}

.values-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.value-card {
  text-align: center;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 10px;
  transition: transform 0.3s ease;
}

.value-card:hover {
  transform: translateY(-5px);
}

.value-card i {
  font-size: 2rem;
  color: #ff69b4;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .about-story {
    flex-direction: column;
  }
  
  .values-container {
    grid-template-columns: 1fr;
  }
}

/* Animations */
@keyframes slideIn {
  0% {
    transform: translateY(-100%);
  }
  100% {
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

@keyframes slideInRight {
  0% {
    transform: translateX(100%);
  }
  100% {
    transform: translateX(0);
  }
}

/* Media Queries for responsiveness */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    padding: 15px 10px;
    align-items: center;
  }

  .logo {
    font-size: 1.6em;
    text-align: center;
  }

  .nav-links {
    flex-direction: column;
    gap: 10px;
    font-size: 1em;
  }

  .hero {
    flex-direction: column;
    padding: 20px;
  }

  .hero-text {
    max-width: 100%;
    text-align: center;
  }

  .hero-text h1 {
    font-size: 2.5em;
  }

  .hero-text p {
    font-size: 1em;
  }

  .hero-image {
    max-width: 100%;
    margin-top: 20px;
  }

  .footer-info {
    display: block;
  }

  .footer-info div {
    margin-bottom: 20px;
  }
}

@media (max-width: 480px) {
  .header {
    padding: 10px 5px;
  }

  .logo {
    font-size: 1.9em;
  }

  .nav-links {
    flex-direction: column;
    gap: 8px;
    font-size: 1.1em;
  }

  .nav-links a {
    font-size: 1em;
    text-align: center;
    color: white;
  }

  .nav-links a:hover {
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
  }

  .hero-text h1 {
    font-size: 2em;
  }

  .hero-text p {
    font-size: 0.9em;
  }

  .footer-info h4 {
    font-size: 1.5em;
  }

  .footer-info p {
    font-size: 1em;
  }

  .get-now-btn,
  .play-video-btn {
    width: 100%;
    margin-top: 10px;
  }
}

.coffee-list-move {
  transition: transform 0.5s;
}

.coffee-card {
  transition: all 0.3s;
}

.coffee-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.category {
  color: #666;
  font-size: 0.9em;
  margin: 5px 0;
}

.filter-menu span {
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s;
}

.filter-menu span:hover {
  background-color: #f4a261;
  color: white;
}

.filter-menu span.active {
  background-color: #f4a261;
  color: white;
}

.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 5px;
  color: white;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.success {
  background-color: #4caf50;
}

.error {
  background-color: #ff4444;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Video Modal Styles */
.video-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 0;
}

.video-container {
  position: relative;
  width: 100%;
  height: 100%;
  max-width: 500px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.video-container video {
  width: 100%;
  height: auto;
  max-height: 90vh;
  object-fit: contain;
  background: #000;
}

.close-video {
  position: absolute;
  top: 20px;
  right: 20px;
  background-color: rgba(0, 0, 0, 0.5);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.close-video:hover {
  opacity: 0.8;
}

@media (max-width: 768px) {
  .video-modal {
    background-color: #000;
  }
  
  .video-container {
    width: 100%;
    max-width: none;
    padding: 0 20px;
  }
  
  .video-container video {
    width: 100%;
    height: auto;
    max-height: 80vh;
    object-fit: contain;
  }
}

.cafe-logo {
  height: 50px;
  margin-right: 10px;
  vertical-align: middle;
  box-shadow: none;
  transition: transform 0.3s ease;
}

.hero-logo {
  height: 100px;
  margin-top: 20px;
  margin-left: 20px;
  vertical-align: middle;
  box-shadow: none;
  transition: transform 0.3s ease;
}

/* Footer Styles */
footer {
  background-color: white;
  color: #3b2a2a;
  padding: 40px 0 20px;
  width: 100%;
  margin-top: auto;
  animation: fadeInUp 0.8s ease-out;
  border-top: 1px solid #eee;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
  flex-wrap: wrap;
  gap: 30px;
}

.footer-section {
  flex: 1;
  min-width: 200px;
  margin-bottom: 20px;
  padding: 0 15px;
  animation: fadeInUp 0.8s ease-out;
  animation-fill-mode: both;
}

.footer-section:nth-child(1) {
  animation-delay: 0.1s;
}

.footer-section:nth-child(2) {
  animation-delay: 0.3s;
}

.footer-section:nth-child(3) {
  animation-delay: 0.5s;
}

.footer-section:nth-child(4) {
  animation-delay: 0.7s;
}

.footer-section h3 {
  color: #d88e8e;
  margin-bottom: 15px;
  font-size: 1.1rem;
  font-weight: 600;
  position: relative;
  display: inline-block;
}

.footer-section h3::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: -4px;
  left: 0;
  background-color: #d88e8e;
  transition: width 0.3s ease;
}

.footer-section:hover h3::after {
  width: 100%;
}

.footer-section p {
  margin-bottom: 8px;
  line-height: 1.5;
  font-size: 0.95rem;
  color: #666;
  transition: transform 0.3s ease;
}

.footer-section p:hover {
  transform: translateX(5px);
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section ul li {
  margin-bottom: 8px;
  transition: transform 0.3s ease;
}

.footer-section ul li:hover {
  transform: translateX(5px);
}

.footer-section ul li a {
  color: #666;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  font-size: 0.95rem;
  position: relative;
  display: inline-block;
}

.footer-section i {
  margin-right: 8px;
  color: #d88e8e;
  width: 16px;
  transition: transform 0.3s ease;
}

.footer-section p:hover i {
  transform: scale(1.2);
}

.social-icons {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
}

.social-icons a {
  color: #666;
  font-size: 1.5rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.social-icons a:hover {
  color: #d88e8e;
  transform: translateY(-3px);
}

.social-icons a::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: #d88e8e;
  opacity: 0.2;
  transform: scale(0);
  transition: transform 0.3s ease;
}

.social-icons a:hover::after {
  transform: scale(1.5);
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  margin-top: 30px;
  border-top: 1px solid rgba(59, 42, 42, 0.1);
  animation: fadeIn 1s ease-out 1s both;
}

.footer-bottom p {
  font-size: 0.85rem;
  color: #666;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@media screen and (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .footer-section {
    margin-bottom: 20px;
    min-width: 100%;
  }
  
  .social-icons {
    justify-content: center;
  }

  .footer-section ul li {
    margin-bottom: 6px;
  }

  .footer-section h3::after {
    left: 50%;
    transform: translateX(-50%);
  }

  .footer-section p:hover,
  .footer-section ul li:hover {
    transform: translateY(-3px);
  }
}

@media screen and (max-width: 480px) {
  footer {
    padding: 30px 0 15px;
  }

  .footer-section h3 {
    font-size: 1rem;
  }

  .footer-section p,
  .footer-section ul li a {
    font-size: 0.9rem;
  }

  .social-icons a {
    font-size: 1.3rem;
  }
}

/* Add these styles before the @media queries */
.team-section {
  margin-top: 4rem;
  text-align: center;
}

.team-section h3 {
  color: #333;
  margin-bottom: 2rem;
  font-size: 2rem;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 1rem;
}

.team-member {
  background-color: #fce6e6;
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.team-member:hover {
  transform: translateY(-5px);
}

.team-member img {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 1rem;
  border: 4px solid #fff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.team-member h4 {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.team-member .role {
  color: #d88e8e;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.team-member .description {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .team-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .team-member img {
    width: 120px;
    height: 120px;
  }
}

.contact-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  background-color: #fff5f5;
}

.contact-container {
  background-color: #fff;
  border-radius: 10px;
  padding: 3rem;
}

.contact-header {
  text-align: center;
  margin-bottom: 3rem;
}

.contact-header h2 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 1rem;
}

.contact-header p {
  color: #666;
  font-size: 1.1rem;
}

.contact-content {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  margin: 0 auto;
  max-width: 1200px;
}

.contact-info-card {
  background-color: #fff;
  padding: 2rem;
  text-align: center;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.contact-info-card:hover {
  transform: translateY(-5px);
}

.icon-circle {
  width: 80px;
  height: 80px;
  background-color: #fff2f2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  transition: all 0.3s ease;
}

.icon-circle i {
  font-size: 2rem;
  color: #e57373;
  transition: all 0.3s ease;
}

.contact-info-card:hover .icon-circle {
  background-color: #e57373;
}

.contact-info-card:hover .icon-circle i {
  color: #fff;
  transform: rotate(360deg);
}

.contact-info-card h3 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.contact-info-card p {
  color: #666;
  margin: 0.5rem 0;
  font-size: 0.95rem;
  line-height: 1.6;
}

.contact-form-container {
  grid-column: 1 / -1;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-top: 2rem;
}

.contact-form-container h3 {
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
}

.contact-form .form-group {
  margin-bottom: 1rem;
}

.contact-form label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-size: 0.9rem;
}

.contact-form input,
.contact-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  background-color: #fff;
}

.contact-form textarea {
  resize: vertical;
  min-height: 120px;
}

.btn-primary {
  background-color: #d88e8e;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  width: 100%;
  transition: background-color 0.3s ease;
  margin-top: 1rem;
}

.btn-primary:hover {
  background-color: #c27b7b;
}

@media (max-width: 1200px) {
  .contact-content {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .contact-content {
    grid-template-columns: 1fr;
  }
  
  .contact-container {
    padding: 1.5rem;
  }
}
</style>