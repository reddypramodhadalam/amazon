package rbs.page;

import org.openqa.selenium.WebElement;

public class LoginPage {
	
	String  mobileID = "id==username";
	String passwordField = "id==password";
	String loginButton = "id==loginButton";
	String userIcon = "id==userIcon";
	String passwordIcon = "id==com.ctl.max2:id/passwordIcon";
	
	public String getMobileID() {
		return mobileID;
	}
	
	public String getPasswordField() {
		return passwordField;
	}
	
	public String getLoginButton() {
		return loginButton;
	}
}
