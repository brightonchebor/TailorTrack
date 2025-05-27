// Global variables
let orders = [];
let customers = [];
let currentTab = "dashboard";

// Initialize the application
document.addEventListener("DOMContentLoaded", function () {
  loadSampleData();
  updateDashboard();
  displayOrders();

  // Set minimum date to today for due date
  const today = new Date().toISOString().split("T")[0];
  document.getElementById("dueDate").min = today;

  // Auto-calculate balance
  document
    .getElementById("totalCost")
    .addEventListener("input", calculateBalance);
  document
    .getElementById("amountPaid")
    .addEventListener("input", calculateBalance);

  // Search functionality
  document
    .getElementById("searchInput")
    .addEventListener("input", handleSearch);

  // Apply filters when changed
  document
    .getElementById("statusFilter")
    .addEventListener("change", applyFilters);
  document
    .getElementById("sortFilter")
    .addEventListener("change", applyFilters);
});

// Sample data for demonstration
function loadSampleData() {
  const sampleOrders = [
    {
      id: 1,
      customerName: "Kevin Oduor",
      phoneNumber: "+254787654321",
      whatsappNumber: "+254787654321",
      orderDate: "2024-11-01",
      dueDate: "2024-11-15",
      status: "progress",
      measurements: {
        bust: 36,
        waist: 28,
        hips: 38,
        length: 40,
        notes: "Slightly loose fitting preferred",
      },
      designNotes: "Traditional saree blouse with gold thread work",
      totalCost: 2500,
      amountPaid: 1000,
      balance: 1500,
    },
    {
      id: 2,
      customerName: "Nyaboke Patel",
      phoneNumber: "+25473456789",
      whatsappNumber: "25473456789",
      orderDate: "2024-11-05",
      dueDate: "2024-11-10",
      status: "completed",
      measurements: {
        bust: 34,
        waist: 26,
        hips: 36,
        length: 38,
        notes: "Standard fit",
      },
      designNotes: "Simple kurti with minimal embroidery",
      totalCost: 1800,
      amountPaid: 1800,
      balance: 0,
    },
    {
      id: 3,
      customerName: "Maureen Gupta",
      phoneNumber: "+24578887776",
      whatsappNumber: "+24578887776",
      orderDate: "2024-10-28",
      dueDate: "2024-11-08",
      status: "pending",
      measurements: {
        bust: 38,
        waist: 30,
        hips: 40,
        length: 42,
        notes: "Extra room in waist area",
      },
      designNotes: "Wedding lehenga with heavy work",
      totalCost: 15000,
      amountPaid: 5000,
      balance: 10000,
    },
  ];

  orders = sampleOrders;

  // Extract unique customers
  customers = orders
    .map((order) => ({
      name: order.customerName,
      phone: order.phoneNumber,
      whatsapp: order.whatsappNumber,
      totalOrders: orders.filter((o) => o.customerName === order.customerName)
        .length,
      totalSpent: orders
        .filter((o) => o.customerName === order.customerName)
        .reduce((sum, o) => sum + o.amountPaid, 0),
    }))
    .filter(
      (customer, index, self) =>
        index === self.findIndex((c) => c.phone === customer.phone)
    );
}

// Tab switching functionality
function switchTab(tabName) {
  // Hide all tab contents
  document.querySelectorAll(".tab-content").forEach((tab) => {
    tab.classList.remove("active");
  });

  // Remove active class from all tab links
  document.querySelectorAll(".tab-link").forEach((link) => {
    link.classList.remove("active");
  });

  // Show selected tab content
  document.getElementById(tabName).classList.add("active");

  // Add active class to clicked tab link
  event.target.classList.add("active");

  currentTab = tabName;

  // Load content based on tab
  switch (tabName) {
    case "dashboard":
      updateDashboard();
      break;
    case "orders":
      displayAllOrders();
      break;
    case "customers":
      displayCustomers();
      break;
    case "payments":
      displayPayments();
      break;
  }
}

// Update dashboard statistics
function updateDashboard() {
  const totalOrders = orders.length;
  const activeOrders = orders.filter(
    (order) => order.status !== "delivered"
  ).length;
  const overdueOrders = orders.filter((order) => {
    const dueDate = new Date(order.dueDate);
    const today = new Date();
    return (
      dueDate < today &&
      order.status !== "completed" &&
      order.status !== "delivered"
    );
  }).length;
  const totalRevenue = orders.reduce((sum, order) => sum + order.amountPaid, 0);

  document.getElementById("totalOrders").textContent = totalOrders;
  document.getElementById("activeOrders").textContent = activeOrders;
  document.getElementById("overdueOrders").textContent = overdueOrders;
  document.getElementById(
    "totalRevenue"
  ).textContent = `₹${totalRevenue.toLocaleString()}`;

  // Display recent orders
  const recentOrders = orders.slice(-5).reverse();
  displayOrdersInGrid("recentOrdersGrid", recentOrders);
}

// Display orders in grid
function displayOrdersInGrid(gridId, ordersToDisplay) {
  const grid = document.getElementById(gridId);

  if (ordersToDisplay.length === 0) {
    grid.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📋</div>
                        <h3>No orders found</h3>
                        <p>Create your first order to get started!</p>
                    </div>
                `;
    return;
  }

  grid.innerHTML = ordersToDisplay
    .map((order) => {
      const isOverdue =
        new Date(order.dueDate) < new Date() &&
        order.status !== "completed" &&
        order.status !== "delivered";

      return `
                    <div class="order-card ${
                      isOverdue ? "overdue" : ""
                    }" onclick="viewOrderDetails(${order.id})">
                        <div class="order-header">
                            <div class="customer-name">${
                              order.customerName
                            }</div>
                            <div class="order-status status-${order.status}">${
        order.status
      }</div>
                        </div>
                        <div class="order-details">
                            <div class="detail-row">
                                <span class="detail-label">Order Date:</span>
                                <span class="detail-value">${formatDate(
                                  order.orderDate
                                )}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Due Date:</span>
                                <span class="detail-value ${
                                  isOverdue ? "balance-amount" : ""
                                }">${formatDate(order.dueDate)}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Phone:</span>
                                <span class="detail-value">${
                                  order.phoneNumber
                                }</span>
                            </div>
                        </div>
                        <div class="payment-info">
                            <div class="detail-row">
                                <span class="detail-label">Total:</span>
                                <span class="detail-value">KES${order.totalCost.toLocaleString()}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Paid:</span>
                                <span class="detail-value paid-amount">KES${order.amountPaid.toLocaleString()}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Balance:</span>
                                <span class="detail-value balance-amount">KES${order.balance.toLocaleString()}</span>
                            </div>
                        </div>
                    </div>
                `;
    })
    .join("");
}

// Display all orders
function displayAllOrders() {
  displayOrdersInGrid("allOrdersGrid", orders);
}

function displayOrders() {
  if (currentTab === "dashboard") {
    updateDashboard();
  } else if (currentTab === "orders") {
    displayAllOrders();
  }
}

// Display customers
function displayCustomers() {
  const grid = document.getElementById("customersGrid");

  if (customers.length === 0) {
    grid.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">👥</div>
                        <h3>No customers yet</h3>
                        <p>Customers will appear here once you create orders.</p>
                    </div>
                `;
    return;
  }

  grid.innerHTML = customers
    .map(
      (customer) => `
                <div class="order-card">
                    <div class="order-header">
                        <div class="customer-name">${customer.name}</div>
                        <div class="order-status status-progress">${
                          customer.totalOrders
                        } orders</div>
                    </div>
                    <div class="order-details">
                        <div class="detail-row">
                            <span class="detail-label">Phone:</span>
                            <span class="detail-value">${customer.phone}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">WhatsApp:</span>
                            <span class="detail-value">${
                              customer.whatsapp
                            }</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Total Spent:</span>
                            <span class="detail-value paid-amount">KES${customer.totalSpent.toLocaleString()}</span>
                        </div>
                    </div>
                </div>
            `
    )
    .join("");
}

// Display payments
function displayPayments() {
  const grid = document.getElementById("paymentsGrid");
  const pendingPayments = orders.filter((order) => order.balance > 0);

  if (pendingPayments.length === 0) {
    grid.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">💰</div>
                        <h3>All payments up to date!</h3>
                        <p>No pending payments at the moment.</p>
                    </div>
                `;
    return;
  }

  grid.innerHTML = pendingPayments
    .map(
      (order) => `
                <div class="order-card">
                    <div class="order-header">
                        <div class="customer-name">${order.customerName}</div>
                        <div class="order-status status-pending">Pending</div>
                    </div>
                    <div class="order-details">
                        <div class="detail-row">
                            <span class="detail-label">Phone:</span>
                            <span class="detail-value">${
                              order.phoneNumber
                            }</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Due Date:</span>
                            <span class="detail-value">${formatDate(
                              order.dueDate
                            )}</span>
                        </div>
                    </div>
                    <div class="payment-info">
                        <div class="detail-row">
                            <span class="detail-label">Total Cost:</span>
                            <span class="detail-value">KES${order.totalCost.toLocaleString()}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Paid:</span>
                            <span class="detail-value paid-amount">KES${order.amountPaid.toLocaleString()}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Outstanding:</span>
                            <span class="detail-value balance-amount">KES${order.balance.toLocaleString()}</span>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="btn btn-primary" onclick="recordPayment(${
                          order.id
                        })">Record Payment</button>
                    </div>
                </div>
            `
    )
    .join("");
}

// Modal functions
function openNewOrderModal() {
  document.getElementById("newOrderModal").style.display = "block";
}

function closeNewOrderModal() {
  document.getElementById("newOrderModal").style.display = "none";
  document.getElementById("newOrderForm").reset();
}

// Form submission
document
  .getElementById("newOrderForm")
  .addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = {
      id: orders.length + 1,
      customerName: document.getElementById("customerName").value,
      phoneNumber: document.getElementById("phoneNumber").value,
      whatsappNumber:
        document.getElementById("whatsappNumber").value ||
        document.getElementById("phoneNumber").value,
      orderDate: new Date().toISOString().split("T")[0],
      dueDate: document.getElementById("dueDate").value,
      status: document.getElementById("orderStatus").value,
      measurements: {
        bust: parseFloat(document.getElementById("bust").value) || 0,
        waist: parseFloat(document.getElementById("waist").value) || 0,
        hips: parseFloat(document.getElementById("hips").value) || 0,
        length: parseFloat(document.getElementById("length").value) || 0,
        notes: document.getElementById("measurementNotes").value,
      },
      designNotes: document.getElementById("designNotes").value,
      totalCost: parseFloat(document.getElementById("totalCost").value),
      amountPaid: parseFloat(document.getElementById("amountPaid").value) || 0,
      balance:
        parseFloat(document.getElementById("totalCost").value) -
        (parseFloat(document.getElementById("amountPaid").value) || 0),
    };

    orders.push(formData);

    // Update customers array
    const existingCustomer = customers.find(
      (c) => c.phone === formData.phoneNumber
    );
    if (!existingCustomer) {
      customers.push({
        name: formData.customerName,
        phone: formData.phoneNumber,
        whatsapp: formData.whatsappNumber,
        totalOrders: 1,
        totalSpent: formData.amountPaid,
      });
    } else {
      existingCustomer.totalOrders++;
      existingCustomer.totalSpent += formData.amountPaid;
    }

    closeNewOrderModal();
    updateDashboard();
    displayOrders();

    // Show success message
    alert("Order created successfully!");
  });

// Auto-calculate balance
function calculateBalance() {
  const totalCost = parseFloat(document.getElementById("totalCost").value) || 0;
  const amountPaid =
    parseFloat(document.getElementById("amountPaid").value) || 0;
  const balance = totalCost - amountPaid;

  // Update balance display if there's a balance field
  if (document.getElementById("balanceAmount")) {
    document.getElementById(
      "balanceAmount"
    ).textContent = `₹${balance.toLocaleString()}`;
  }
}

// Search functionality
function handleSearch() {
  const searchTerm = document.getElementById("searchInput").value.toLowerCase();
  let filteredOrders = orders;

  if (searchTerm) {
    filteredOrders = orders.filter(
      (order) =>
        order.customerName.toLowerCase().includes(searchTerm) ||
        order.phoneNumber.includes(searchTerm) ||
        order.whatsappNumber.includes(searchTerm)
    );
  }

  if (currentTab === "dashboard") {
    displayOrdersInGrid("recentOrdersGrid", filteredOrders.slice(-5).reverse());
  } else if (currentTab === "orders") {
    displayOrdersInGrid("allOrdersGrid", filteredOrders);
  }
}

// Apply filters
function applyFilters() {
  let filteredOrders = [...orders];

  const statusFilter = document.getElementById("statusFilter").value;
  const sortFilter = document.getElementById("sortFilter").value;

  // Apply status filter
  if (statusFilter) {
    filteredOrders = filteredOrders.filter(
      (order) => order.status === statusFilter
    );
  }

  // Apply sorting
  switch (sortFilter) {
    case "date_desc":
      filteredOrders.sort(
        (a, b) => new Date(b.orderDate) - new Date(a.orderDate)
      );
      break;
    case "date_asc":
      filteredOrders.sort(
        (a, b) => new Date(a.orderDate) - new Date(b.orderDate)
      );
      break;
    case "due_date":
      filteredOrders.sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));
      break;
    case "customer":
      filteredOrders.sort((a, b) =>
        a.customerName.localeCompare(b.customerName)
      );
      break;
  }

  displayOrdersInGrid("allOrdersGrid", filteredOrders);
}

// View order details
function viewOrderDetails(orderId) {
  const order = orders.find((o) => o.id === orderId);
  if (!order) return;

  alert(`Order Details for ${order.customerName}:
            
Phone: ${order.phoneNumber}
Order Date: ${formatDate(order.orderDate)}
Due Date: ${formatDate(order.dueDate)}
Status: ${order.status.toUpperCase()}

Measurements:
- Bust/Chest: ${order.measurements.bust}"
- Waist: ${order.measurements.waist}"
- Hips: ${order.measurements.hips}"
- Length: ${order.measurements.length}"
- Notes: ${order.measurements.notes}

Design Notes: ${order.designNotes}

Payment:
- Total Cost: ₹${order.totalCost.toLocaleString()}
- Amount Paid: ₹${order.amountPaid.toLocaleString()}
- Balance: ₹${order.balance.toLocaleString()}`);
}

// Record payment
function recordPayment(orderId) {
  const order = orders.find((o) => o.id === orderId);
  if (!order) return;

  const payment = prompt(`Record payment for ${order.customerName}
Outstanding balance: ₹${order.balance.toLocaleString()}

Enter payment amount:`);

  if (payment && !isNaN(payment) && parseFloat(payment) > 0) {
    const paymentAmount = parseFloat(payment);

    if (paymentAmount > order.balance) {
      alert("Payment amount cannot exceed the outstanding balance!");
      return;
    }

    order.amountPaid += paymentAmount;
    order.balance -= paymentAmount;

    // Update customer total spent
    const customer = customers.find((c) => c.phone === order.phoneNumber);
    if (customer) {
      customer.totalSpent += paymentAmount;
    }

    updateDashboard();
    displayPayments();
    alert(
      `Payment of ₹${paymentAmount.toLocaleString()} recorded successfully!`
    );
  }
}

// Utility function to format dates
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

// Close modal when clicking outside
window.onclick = function (event) {
  const modal = document.getElementById("newOrderModal");
  if (event.target === modal) {
    closeNewOrderModal();
  }
};

// Handle file upload display
document
  .getElementById("designUpload")
  .addEventListener("change", function (e) {
    const files = e.target.files;
    const uploadDiv = e.target.parentElement;

    if (files.length > 0) {
      const fileNames = Array.from(files)
        .map((file) => file.name)
        .join(", ");
      uploadDiv.innerHTML = `
                    <div>📎 ${files.length} file(s) selected</div>
                    <div style="font-size: 0.8rem; color: #666; margin-top: 5px;">${fileNames}</div>
                    <input type="file" id="designUpload" multiple accept="image/*,.pdf">
                `;
    }
  });

// Auto-save form data to prevent loss (using sessionStorage simulation)
let formAutoSave = {};

function autoSaveForm() {
  const formElements = document.querySelectorAll(
    "#newOrderForm input, #newOrderForm select, #newOrderForm textarea"
  );
  formElements.forEach((element) => {
    element.addEventListener("input", function () {
      formAutoSave[element.id] = element.value;
    });
  });
}

// Initialize auto-save
setTimeout(autoSaveForm, 1000);

// Keyboard shortcuts
document.addEventListener("keydown", function (e) {
  // Ctrl+N or Cmd+N for new order
  if ((e.ctrlKey || e.metaKey) && e.key === "n") {
    e.preventDefault();
    openNewOrderModal();
  }

  // Escape to close modal
  if (e.key === "Escape") {
    closeNewOrderModal();
  }
});

// Service Worker registration for offline functionality (basic setup)
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    // Note: In a real implementation, you would create a service worker file
    console.log("Service Worker support detected");
  });
}
