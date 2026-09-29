// Main Application JavaScript
document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alert banners after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Toggle Sidebar on Mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    if (sidebarToggle && sidebarWrapper) {
        sidebarToggle.addEventListener('click', function (e) {
            e.preventDefault();
            sidebarWrapper.classList.toggle('d-none');
        });
    }
});
