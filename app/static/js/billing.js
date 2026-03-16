/**
 * Billing page dynamic product-row management.
 */

let rowCount = 1;

function addProductRow() {
    const container = document.getElementById("productRows");
    const row = document.createElement("div");
    row.className = "product-row";
    row.innerHTML =
        '<input type="text" name="product_id_' + rowCount + '" placeholder="Product ID" required>' +
        '<input type="number" name="quantity_' + rowCount + '" placeholder="Quantity" min="1" required>' +
        '<button type="button" class="btn-remove" onclick="removeRow(this)">&times;</button>';
    container.appendChild(row);
    rowCount++;
}

function removeRow(button) {
    const rows = document.querySelectorAll(".product-row");
    if (rows.length > 1) {
        button.parentElement.remove();
        reindexRows();
    }
}

function reindexRows() {
    const rows = document.querySelectorAll(".product-row");
    rows.forEach(function (row, index) {
        const inputs = row.querySelectorAll("input");
        inputs[0].name = "product_id_" + index;
        inputs[1].name = "quantity_" + index;
    });
    rowCount = rows.length;
}
