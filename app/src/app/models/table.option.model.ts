export class TableOption {
	NAME: string;
	HEADER: string[];
	API: any;

	constructor(arg1: string, arg2: string[], arg3: any) {
		this.NAME = arg1;
		this.HEADER = arg2;
		this.API = arg3;
	}
}
