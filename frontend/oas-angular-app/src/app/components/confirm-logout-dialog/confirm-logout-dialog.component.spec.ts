import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfirmLogoutDialogComponent } from './confirm-logout-dialog.component';

describe('ConfirmLogoutDialogComponent', () => {
  let component: ConfirmLogoutDialogComponent;
  let fixture: ComponentFixture<ConfirmLogoutDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ConfirmLogoutDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConfirmLogoutDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
