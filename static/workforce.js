document.addEventListener(
    "DOMContentLoaded",
    () => {

        const searchInput =
            document.getElementById(
                "employeeSearch"
            );

        const roleFilter =
            document.getElementById(
                "employeeRoleFilter"
            );

        const rows =
            Array.from(
                document.querySelectorAll(
                    ".workforce-row"
                )
            );

        const noResults =
            document.getElementById(
                "employeeNoResults"
            );


        if (
            !searchInput
            || !roleFilter
            || rows.length === 0
        ) {
            return;
        }


        function filterEmployees() {

            const searchValue =
                searchInput.value
                    .trim()
                    .toLowerCase();


            const selectedRole =
                roleFilter.value
                    .trim()
                    .toLowerCase();


            let visibleCount = 0;


            rows.forEach(
                (row) => {

                    const searchable =
                        (
                            row.dataset.search
                            || ""
                        )
                        .toLowerCase();


                    const employeeRole =
                        (
                            row.dataset.role
                            || ""
                        )
                        .toLowerCase();


                    const matchesSearch =
                        searchValue === ""
                        || searchable.includes(
                            searchValue
                        );


                    const matchesRole =
                        selectedRole === "all"
                        || employeeRole
                            === selectedRole;


                    const shouldShow =
                        matchesSearch
                        && matchesRole;


                    row.hidden =
                        !shouldShow;


                    if (shouldShow) {
                        visibleCount += 1;
                    }

                }
            );


            if (noResults) {

                noResults.hidden =
                    visibleCount !== 0;

            }

        }


        searchInput.addEventListener(
            "input",
            filterEmployees
        );


        roleFilter.addEventListener(
            "change",
            filterEmployees
        );

    }
);