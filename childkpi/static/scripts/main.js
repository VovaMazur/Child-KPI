//datepicker form
const aboveForm = document.getElementById("dateform");
aboveForm.addEventListener("change", () => {
    aboveForm.submit();
    });

//change active date by clicking on the main table row
const homeTable = document.getElementById("home_table");
homeTable.addEventListener("click", (e) => {
    aboveForm.firstElementChild.value = e.target.parentElement.firstElementChild.innerText;
    aboveForm.submit();
})
