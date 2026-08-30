/* ============================================================
   MEDSECURE DASHBOARD JAVASCRIPT
   Final dashboard behaviour
============================================================ */

document.addEventListener("DOMContentLoaded", () => {

    /* ========================================================
       1. TIME-AWARE ADMIN GREETING

       Keeps the top navigation name unchanged.
       Greeting appears inside the admin dashboard above
       "MedSecure Administration".
    ======================================================== */

    const greetingElement =
        document.getElementById("dashboardGreeting");


    if (greetingElement) {

        const userName =
            (greetingElement.dataset.userName || "").trim();


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


        greetingElement.textContent =
            userName
                ? `${greeting}, ${userName}`
                : greeting;

    }


    /* ========================================================
       2. PATIENT SEARCH + ALLERGY FILTER

       Used by Nurse / Doctor dashboard.
       Does nothing on Admin or Patient dashboard.
    ======================================================== */

    const patientSearch =
        document.getElementById("patientSearch");

    const patientFilter =
        document.getElementById("patientFilter");

    const patientList =
        document.getElementById("patientList");

    const noPatientsFound =
        document.getElementById("noPatientsFound");


    if (
        patientSearch &&
        patientFilter &&
        patientList
    ) {

        const patientRows =
            Array.from(
                patientList.querySelectorAll(
                    ".patient-worklist-row"
                )
            );


        const updatePatientList = () => {

            const searchValue =
                patientSearch.value
                    .trim()
                    .toLowerCase();


            const filterValue =
                patientFilter.value;


            let visibleCount = 0;


            patientRows.forEach((row) => {

                const patientName =
                    (row.dataset.name || "")
                        .toLowerCase();


                const patientId =
                    (row.dataset.patientId || "")
                        .toLowerCase();


                const alertState =
                    row.dataset.alert || "clear";


                const matchesSearch =
                    searchValue === "" ||
                    patientName.includes(searchValue) ||
                    patientId.includes(searchValue);


                const matchesFilter =
                    filterValue === "all" ||
                    alertState === filterValue;


                const shouldShow =
                    matchesSearch &&
                    matchesFilter;


                row.hidden =
                    !shouldShow;


                if (shouldShow) {

                    visibleCount += 1;

                }

            });


            if (noPatientsFound) {

                noPatientsFound.hidden =
                    visibleCount !== 0;

            }

        };


        patientSearch.addEventListener(
            "input",
            updatePatientList
        );


        patientFilter.addEventListener(
            "change",
            updatePatientList
        );


        updatePatientList();

    }


    /* ========================================================
       3. CLINICAL SIDEBAR ACTIVE STATE
    ======================================================== */

    const sidebarLinks =
        Array.from(
            document.querySelectorAll(
                ".clinical-sidebar-nav .clinical-nav-item"
            )
        );


    sidebarLinks.forEach((link) => {

        link.addEventListener("click", () => {

            sidebarLinks.forEach((item) => {

                item.classList.remove("active");

            });


            link.classList.add("active");

        });

    });

});