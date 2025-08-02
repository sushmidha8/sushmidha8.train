document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const searchForm = document.getElementById('search-form');
    const bookingForm = document.getElementById('booking-form');
    const modal = document.getElementById('confirmation-modal');
    const closeModal = document.querySelector('.close');
    
    // Initialize date picker with today's date
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = today;
        dateInput.min = today;
    }

    // Station Autocomplete
    const sourceInput = document.getElementById('source');
    const destinationInput = document.getElementById('destination');
    
    if (sourceInput && destinationInput) {
        // Fetch stations from API
        fetch('/api/stations')
            .then(response => response.json())
            .then(stations => {
                setupAutocomplete(sourceInput, stations);
                setupAutocomplete(destinationInput, stations);
            })
            .catch(error => console.error('Error loading stations:', error));
    }

    // Booking Form Submission
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Disable button during submission
            const submitBtn = bookingForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            
            // Submit form data
            fetch(bookingForm.action, {
                method: 'POST',
                body: new FormData(bookingForm),
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showConfirmation(data.booking);
                } else {
                    alert('Booking failed: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Booking failed due to technical error');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Confirm Booking';
            });
        });
    }

    // Modal Close Button
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            modal.style.display = 'none';
            window.location.href = '/'; // Redirect to home after closing
        });
    }

    // Click outside modal to close
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
            window.location.href = '/';
        }
    });

    // Helper Functions
    function setupAutocomplete(inputElement, stations) {
        const datalist = document.createElement('datalist');
        datalist.id = `${inputElement.id}-list`;
        stations.forEach(station => {
            const option = document.createElement('option');
            option.value = station;
            datalist.appendChild(option);
        });
        inputElement.parentNode.appendChild(datalist);
        inputElement.setAttribute('list', datalist.id);
    }

    function showConfirmation(bookingData) {
        if (!modal) return;
        
        document.getElementById('confirmation-pnr').textContent = bookingData.pnr;
        document.getElementById('confirmation-train').textContent = bookingData.train_name;
        document.getElementById('confirmation-date').textContent = bookingData.travel_date;
        document.getElementById('confirmation-departure').textContent = bookingData.departure_time;
        document.getElementById('confirmation-seats').textContent = bookingData.seats;
        document.getElementById('confirmation-amount').textContent = `₹${bookingData.total_amount}`;
        
        modal.style.display = 'block';
    }

    // Admin Dashboard Charts
    if (document.getElementById('bookings-chart')) {
        loadDashboardCharts();
    }

    async function loadDashboardCharts() {
        try {
            const response = await fetch('/admin/api/dashboard-stats');
            const data = await response.json();
            
            // Initialize charts using Chart.js
            new Chart(document.getElementById('bookings-chart'), {
                type: 'line',
                data: {
                    labels: data.last_7_days.labels,
                    datasets: [{
                        label: 'Bookings',
                        data: data.last_7_days.values,
                        borderColor: '#3498db',
                        tension: 0.1
                    }]
                }
            });
            
            new Chart(document.getElementById('revenue-chart'), {
                type: 'bar',
                data: {
                    labels: data.top_routes.labels,
                    datasets: [{
                        label: 'Revenue (₹)',
                        data: data.top_routes.values,
                        backgroundColor: '#2ecc71'
                    }]
                }
            });
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }
});