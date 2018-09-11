import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './views/home/home.component';
import { DatabaseComponent } from './views/database/database.component';

const routes: Routes = [
	{ path: '', component: HomeComponent },
	{ path: 'database', component: DatabaseComponent }
];

@NgModule({
	imports: [RouterModule.forRoot(routes)],
	exports: [RouterModule]
})
export class AppRoutingModule { }
