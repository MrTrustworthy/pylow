'use strict';

(function() {

    function handleDragStart(e) {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.dropEffect = 'copy';

        e.dataTransfer.setData('elementid', this.id);
    }

    function handleDragOver(e) {
        if (e.preventDefault) {
            e.preventDefault(); // Necessary. Allows us to drop.
        }
        e.dataTransfer.dropEffect = 'move';  // See the section on the DataTransfer object.
        return false;
    }

    function handleDragEnter(e) {
        // this / e.target is the current hover target.
        this.classList.add('over');
    }

    function handleDragLeave(e) {
        this.classList.remove('over');  // this / e.target is previous target element.
    }

    function handleDrop(e) {
        // this/e.target is current target element.

        if (e.stopPropagation) {
            e.stopPropagation(); // Stops some browsers from redirecting.
        }

        // Set the source column's HTML to the HTML of the column we dropped on.
        let draggedElement = document.getElementById(e.dataTransfer.getData('elementid'));
        draggedElement = draggedElement.cloneNode(true);
        this.appendChild(draggedElement);

        // allow for further dnd'ing
        draggedElement.addEventListener('dragstart', handleDragStart, false);


        // remove previous existing labels for the column name
        let existing = draggedElement.querySelector("[name='" + draggedElement.id + "_target']");
        if (existing !== null){
            draggedElement.removeChild(existing);
        }

        // create a new input with the specified column name
        // TODO FIXME need to remove elements too if attribute is moved multiple times
        let elem = document.createElement('input');
        elem.setAttribute('type', 'hidden');
        elem.setAttribute('name', draggedElement.id + '_target');
        elem.setAttribute('value', this.id);
        draggedElement.appendChild(elem);

        draggedElement.style.opacity = "1.0";

        return false;
    }

    function handleDropDelete(){
        if (e.stopPropagation) {
            e.stopPropagation(); // Stops some browsers from redirecting.
        }
    }


    function setupListeners() {
        let columns = Array.from(document.getElementsByClassName("attribute"));
        columns.forEach((col) => {
            col.addEventListener('dragstart', handleDragStart, false);
        });

        let dropAreaIds = [
            'columns_data',
            'rows_data',
            'color_data',
            'size_data'
        ];
        dropAreaIds.forEach(areaId => {

            let dropArea = document.getElementById(areaId);
            dropArea.addEventListener('drop', handleDrop, false);
            dropArea.addEventListener('dragenter', handleDragEnter, false);
            dropArea.addEventListener('dragover', handleDragOver, false);
            dropArea.addEventListener('dragleave', handleDragLeave, false);
        });
    }

    document.addEventListener("DOMContentLoaded", setupListeners);

})();
