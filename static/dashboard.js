"use strict";

document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("patientSearch");

    const filterSelect =
        document.getElementById("patientFilter");

    const patientRows =
        Array.from(
            document.querySelectorAll(
                ".patient-worklist-row"
            )
        );

    const emptyMessage =
        document.getElementById("noPatientsFound");


    if (
        !searchInput ||
        !filterSelect ||
        patientRows.length === 0
    ) {
        return;
    }


    function updatePatientList() {

        const searchTerm =
            searchInput.value
                .trim()
                .toLowerCase();

        const selectedFilter =
            filterSelect.value;

        let visibleCount = 0;


        patientRows.forEach(function (row) {

            const name =
                row.dataset.name || "";

            const patientId =
                row.dataset.patientId || "";

            const alertState =
                row.dataset.alert || "";


            const matchesSearch =
                name.includes(searchTerm) ||
                patientId.includes(searchTerm);


            const matchesFilter =
                selectedFilter === "all" ||
                alertState === selectedFilter;


            const shouldShow =
                matchesSearch &&
                matchesFilter;


            row.hidden = !shouldShow;


            if (shouldShow) {
                visibleCount++;
            }

        });


        if (emptyMessage) {

            emptyMessage.hidden =
                visibleCount !== 0;

        }

    }


    searchInput.addEventListener(
        "input",
        updatePatientList
    );


    filterSelect.addEventListener(
        "change",
        updatePatientList
    );

});