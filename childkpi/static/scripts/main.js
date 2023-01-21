//datepicker form
const aboveForm = document.getElementById("dateform");
aboveForm.addEventListener("change", () => {
    aboveForm.submit();
    });

//change active date by clicking on the main table row
const homeTable = document.getElementById("home_table");
homeTable.addEventListener("click", (e) => {
    if (e.target.localName !== 'button') {
        const clickedDate = e.target.parentElement.firstElementChild.innerText;
        aboveForm.firstElementChild.value = aboveForm.firstElementChild.value.slice(0,8) + clickedDate;
        aboveForm.submit();
        }
});
