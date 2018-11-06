import { Component, OnInit, Input } from '@angular/core';
import { Table } from '../../models/table.model';

declare var jquery: any;
declare var $: any;
declare var DataTable: any;

@Component({
	selector: 'app-table',
	templateUrl: './table.component.html'
})
export class TableComponent implements OnInit {

	@Input() data: Table;

	constructor() { }

	ngOnInit() {
		$('#dataTable').DataTable({
			'data': this.data.BODY,
			'columns': this.data.HEADER,
			'scrollX': true
		});
	}
}
