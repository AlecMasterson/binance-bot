import { Component, OnInit } from '@angular/core';

import { Table } from '../../models/table.model';
import { TableOption } from '../../models/table.option.model';

import { Balance } from '../../models/balance.model';
import { Policy } from '../../models/policy.model';
import { History } from '../../models/history.model';

import { DatabaseService } from '../../services/database.service';

@Component({
	selector: 'app-database',
	templateUrl: './database.component.html'
})
export class DatabaseComponent implements OnInit {

	private options = [
		new TableOption('Balances', new Balance()._HEADER, function(service) { return service.getBalances() }),
		new TableOption('Trading Policies', new Policy()._HEADER, function(service) { return service.getPolicies() }),
		new TableOption('History', new History()._HEADER, function(service) { return service.getHistory('BNBBTC') }),
	];
	private selected: TableOption;
	private table: Table;
	private loaded = false;
	private loading = false;

	constructor(private databaseService: DatabaseService) { }

	ngOnInit() { }

	select(option) {
		this.selected = option;
		this.refresh();
	}

	refresh() {
		this.loaded = false;
		this.loading = true;
		this.table = new Table([], []);
		this.selected.API(this.databaseService).subscribe((data: any[]) => this.update_table(data));
	}

	update_table(data: any[]) {
		for (var i in this.selected.HEADER) this.table.HEADER.push({ 'title': this.selected.HEADER[i] });

		for (var i in data) {
			this.table.BODY.push(Object.keys(data[i]).map(function(key) {
				return data[i][key];
			}));
		}
		this.loaded = true;
		this.loading = false;
	}

}
