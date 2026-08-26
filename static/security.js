"use strict";

document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("securitySearch");

    const filterSelect =
        document.getElementById("securityFilter");

    const eventRows =
        Array.from(
            document.querySelectorAll(
                ".security-event-row"
            )
        );

    const noResults =
        document.getElementById("securityNoResults");


    if (
        !searchInput ||
        !filterSelect ||
        eventRows.length === 0
    ) {
        return;
    }


    function updateSecurityEvents() {

        const searchTerm =
            searchInput.value
                .trim()
                .toLowerCase();

        const selectedFilter =
            filterSelect.value;

        let visibleCount = 0;


        eventRows.forEach(function (row) {

            const searchableText =
                (row.dataset.search || "")
                    .toLowerCase();

            const outcome =
                (row.dataset.outcome || "")
                    .trim()
                    .toLowerCase();


            const matchesSearch =
                searchableText.includes(
                    searchTerm
                );


            const matchesFilter =
                selectedFilter === "all" ||
                outcome === selectedFilter;


            const shouldShow =
                matchesSearch &&
                matchesFilter;


            row.hidden =
                !shouldShow;


            if (shouldShow) {
                visibleCount++;
            }

        });


        if (noResults) {

            noResults.hidden =
                visibleCount !== 0;

        }

    }


    searchInput.addEventListener(
        "input",
        updateSecurityEvents
    );


    filterSelect.addEventListener(
        "change",
        updateSecurityEvents
    );

});