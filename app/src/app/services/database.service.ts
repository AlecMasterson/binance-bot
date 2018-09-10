import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable()
export class DatabaseService {

	constructor(private http: HttpClient) { }

	getBalances() {
		return this.http.get('http://localhost:3000/get-balances');
	}

	getPolicies() {
		return this.http.get('http://localhost:3000/get-policies');
	}

	getHistory(coinpair) {
		return this.http.get('http://localhost:3000/get-history/' + coinpair);
	}
}
