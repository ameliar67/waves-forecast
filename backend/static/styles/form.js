document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('landing_page_location_form').addEventListener('submit', function (e) {
        e.preventDefault();

        const locationInput = document.getElementById('location_list');
        const selectedOption = document.querySelector(`#options option[value="${locationInput.value}"]`);

        if (selectedOption) {
            const locationId = selectedOption.getAttribute('data-locid');
            const newUrl = `/forecast/${locationId}`;
            console.log("Redirecting to:", newUrl);
            window.location.href = newUrl;
        } else {
            console.log("No matching location found");
            alert("Please select a valid location from the list.");
        }
    })
});