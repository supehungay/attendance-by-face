// static/script.js
function submitForm() {
    showLoading(); // Hiển thị spinner khi bắt đầu submit

    var formData = new FormData(document.getElementById('submit-form'));

    fetch("{{ url_for('submit_form') }}", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        updateTable(data);
        resetForm();
        hideLoading(); // Ẩn spinner khi hoàn thành submit
    })
    .catch(error => {
        console.error('Error:', error);
        hideLoading(); // Ẩn spinner nếu có lỗi xảy ra
    });
}

function showLoading() {
    document.getElementById('loading-spinner').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading-spinner').style.display = 'none';
}

function updateTable(data) {
    var tableBody = document.querySelector('#data-table tbody');
    tableBody.innerHTML = "";

    data.forEach(function(item) {
        var row = tableBody.insertRow();
        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);

        cell1.innerHTML = item['key'];
        cell2.innerHTML = item['value']['Họ tên'];
        cell3.innerHTML = item['value']['Lớp'];
    });
}

function resetForm() {
    // Thiết lập lại giá trị của các trường nhập liệu về giá trị mặc định hoặc trống
    document.getElementById('msv').value = "";
    document.getElementById('name').value = "";
    document.getElementById('class').value = "";
}