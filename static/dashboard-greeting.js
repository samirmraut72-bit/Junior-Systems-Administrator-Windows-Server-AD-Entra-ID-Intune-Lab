/* ============================================================
   MEDSECURE DASHBOARD GREETING
============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    const greetingElement =
        document.getElementById("dashboardGreeting");

    if (!greetingElement) {
        return;
    }


    /*
       First try the name stored directly on the dashboard.
       If unavailable, use the name already shown in the navbar.
    */

    let userName =
        (greetingElement.dataset.userName || "").trim();


    if (!userName) {

        const navbarName =
            document.querySelector(".signed-in-user-name");

        if (navbarName) {
            userName =
                navbarName.textContent.trim();
        }

    }


    const hour =
        new Date().getHours();


    let greeting;


    if (hour >= 5 && hour < 12) {

        greeting = "Good Morning";

    } else if (hour >= 12 && hour < 17) {

        greeting = "Good Afternoon";

    } else {

        greeting = "Good Evening";

    }


    if (userName) {

        greetingElement.textContent =
            greeting + ", " + userName;

    } else {

        greetingElement.textContent =
            greeting;

    }

});