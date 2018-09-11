import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './/app-routing.module';

import { AngularFontAwesomeModule } from 'angular-font-awesome';

import { AppComponent } from './app.component';

import { HomeComponent } from './views/home/home.component';
import { DatabaseComponent } from './views/database/database.component';

import { NavbarComponent } from './components/navbar/navbar.component';
import { LoginComponent } from './components/login/login.component';
import { TableComponent } from './components/table/table.component';

import { DatabaseService } from './services/database.service';

@NgModule({
	declarations: [
		AppComponent,
		HomeComponent,
		DatabaseComponent,
		NavbarComponent,
		LoginComponent,
		TableComponent
	],
	imports: [
		BrowserModule,
		HttpClientModule,
		AppRoutingModule,
		AngularFontAwesomeModule
	],
	providers: [DatabaseService],
	bootstrap: [AppComponent]
})
export class AppModule { }
