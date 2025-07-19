// pagination.js

let halamanAktif = 1;
let dataPerPage = 5;

function setPaginationConfig(config) {
    halamanAktif = config.halamanAktif || 1;
    dataPerPage = config.dataPerPage || 5;
}

function getPaginationConfig() {
    return { halamanAktif, dataPerPage };
}

function changePage(page, callbackRenderTable) {
    halamanAktif = page;
    callbackRenderTable();
}

function ubahdataPerPage() {
    setPaginationConfig({ dataPerPage: parseInt($("#dataPerPageSelect").val()), halamanAktif: 1 });
    renderTable();
}


    $('.filter-input').on('input', function() {
    halamanAktif = 1; 
    renderTable();
});

function renderPagination(totalItems, callbackRenderTable) {
    const pageCount = Math.ceil(totalItems / dataPerPage);
    const pagination = $('#pagination');
    pagination.empty();

    const maxVisiblePages = 5;
    let startPage = Math.max(1, halamanAktif - Math.floor(maxVisiblePages / 2));
    let endPage = startPage + maxVisiblePages - 1;

    if (endPage > pageCount) {
        endPage = pageCount;
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    if (halamanAktif > 1) {
        pagination.append(`
            <li class="page-item">
                <a href="#" class="page-link" onclick="changePage(1, ${callbackRenderTable.name})">First</a>
            </li>
        `);
    }

    if (startPage > 1) {
        pagination.append(`<li class="page-item disabled"><span class="page-link">...</span></li>`);
    }

    for (let i = startPage; i <= endPage; i++) {
        pagination.append(`
            <li class="page-item ${i === halamanAktif ? 'active' : ''}">
                <a href="#" class="page-link" onclick="changePage(${i}, ${callbackRenderTable.name})">${i}</a>
            </li>
        `);
    }

    if (endPage < pageCount) {
        pagination.append(`<li class="page-item disabled"><span class="page-link">...</span></li>`);
    }

    if (halamanAktif < pageCount) {
        pagination.append(`
            <li class="page-item">
                <a href="#" class="page-link" onclick="changePage(${pageCount}, ${callbackRenderTable.name})">Last</a>
            </li>
        `);
    }
}

