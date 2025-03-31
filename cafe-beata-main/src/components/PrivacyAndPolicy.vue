<template>
  <div class="policy-page">
    <div class="policy-container">
      <h1>Privacy and Policy</h1>
      
      <p>Welcome to <strong>UIC Cafe Beàta</strong>. By using our services, you agree to abide by the following terms and conditions. Failure to comply may result in disciplinary actions.</p>
      
      <h2>1. Use of UIC Email</h2>
      <p>All users must register and log in using their official <strong>University of the Immaculate Conception</strong> email. Any attempt to use unauthorized email accounts for ordering will be strictly prohibited, and access may be revoked without notice.</p>
      
      <h2>2. Ordering Guidelines</h2>
      <ul>
        <li><strong>Order Confirmation:</strong> Once an order is placed, it is considered final. No modifications or cancellations will be entertained.</li>
        <li><strong>Item Representation:</strong> The images displayed in the menu are for reference only and may not accurately represent the actual item you will receive upon pickup.</li>
        <li><strong>Order Pickup:</strong> Orders must be picked up within the designated time. Failure to do so will result in the order being forfeited and forwarded to OSAD for documentation.</li>
        <li><strong>Strict Compliance:</strong> Any student failing to collect their order repeatedly will face disciplinary measures, which may include account suspension or further academic penalties.</li>
      </ul>
      
      <h2>3. Payment and Refunds</h2>
      <ul>
        <li><strong>Payment Policy:</strong> All transactions must be completed through the approved payment methods. Failure to pay on time will result in order cancellation.</li>
        <li><strong>Refunds:</strong> Refunds will only be issued under special circumstances, such as system errors or unavailability of items.</li>
      </ul>

      <h2>4. Notifications and Payment Procedure</h2>
      <ul>
        <li><strong>Order Notifications:</strong> While waiting for your order, you can check the <strong>notification button</strong> in the dashboard for updates on your order status.</li>
        <li><strong>Payment:</strong> Once you receive a notification that your order is ready, proceed immediately to the cashier to complete your payment before picking up the order.</li>
        <li><strong>Order Pickup:</strong> After payment is made, you will be able to proceed to pick up your order. Ensure that payment is finalized before picking up the items.</li>
      </ul>

      <h2>5. Code of Conduct</h2>
      <ul>
        <li>Any form of <strong>misuse, fraudulent activities, or abuse</strong> of the ordering system will be taken seriously.</li>
        <li>Attempting to <strong>place fake orders</strong> or misuse someone else's UIC email for transactions will be reported to university authorities.</li>
        <li>Respect for cafe staff and adherence to pick-up schedules is mandatory. Any disrespectful behavior will result in immediate action.</li>
      </ul>
      
      <h2>6. Disciplinary Actions</h2>
      <ol>
        <li><strong>First Offense:</strong> Formal warning and documentation by OSAD.</li>
        <li><strong>Second Offense:</strong> Temporary suspension of ordering privileges.</li>
        <li><strong>Third Offense:</strong> Permanent ban from the UIC Cafe Beàta system, with further disciplinary actions taken by the university.</li>
      </ol>
      
      <h2>7. Changes to Policy</h2>
      <p>UIC Cafe Beàta reserves the right to amend these policies at any time. Users will be notified of any major changes.</p>
      
      <p>By continuing to use this service, you acknowledge that you have read, understood, and agreed to these terms. Failure to comply will result in strict enforcement of the stated guidelines.</p>
      
     <router-link to="/create-account" class="back-link" @click="goBackToCreateAccount">⇦Back</router-link>

    </div>
  </div>
</template>

<script>
export default {
  name: "PrivacyAndPolicy",
  methods: {
    goBackToCreateAccount() {
      // No need to do anything special here as the data is already saved in localStorage
      // and will be restored by the CreateAccountPage component
    }
  }
};
</script>

<style scoped>
/* Background Styling */
.policy-page {
 background-image: url("@/assets/Uicbackroundblur.png"); /* Same as LoginPage.vue */
  background-size: cover;
  background-position: center;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

/* Policy Container Styling */
.policy-container {
  max-width: 700px;
  background: rgba(255, 255, 255, 0.95); /* Soft white with transparency */
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  text-align: justify;
  backdrop-filter: blur(8px); /* Subtle blur effect */
}

/* Headings */
h1 {
  font-size: 28px;
  text-align: center;
  color: #d63384;
  font-weight: bold;
  margin-bottom: 20px;
  text-shadow: 0 0 6px rgba(255, 20, 147, 0.5);
}

h2 {
  color: #c2185b;
  margin-top: 20px;
  font-size: 20px;
  border-left: 5px solid #ff69b4;
  padding-left: 10px;
}

/* Paragraph and List Styling */
p {
  line-height: 1.6;
  color: #444;
  font-size: 16px;
}

ul, ol {
  margin-left: 20px;
}

li {
  margin-bottom: 8px;
  font-size: 15px;
  color: #555;
}

/* Back to Login Link */
.back-link {
  display: block;
  text-align: center;
  margin-top: 25px;
  color: #ff1493;
  text-decoration: none;
  font-weight: bold;
  font-size: 16px;
}

.back-link:hover {
  text-decoration: underline;
  text-shadow: 0 0 5px rgba(255, 20, 147, 0.8);
}

/* Responsive Design */
@media (max-width: 768px) {
  .policy-container {
    width: 90%;
    padding: 20px;
  }

  h1 {
    font-size: 24px;
  }

  h2 {
    font-size: 18px;
  }

  p, li {
    font-size: 14px;
  }
}
</style>
