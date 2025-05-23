/* Additional JavaScript functionality can be added here */
/* The main functionality is already included in the HTML file */

// Custom utility functions
function formatPhoneNumber(phone) {
    if (!phone) return 'N/A';
    // Add any phone formatting logic here
    return phone;
}

function formatCurrency(amount) {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Export utility functions if needed
window.dashboardUtils = {
    formatPhoneNumber,
    formatCurrency
};