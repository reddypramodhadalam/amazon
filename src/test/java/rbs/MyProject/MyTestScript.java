package rbs.MyProject;

import java.util.HashMap;

import org.testng.Reporter;
import org.testng.annotations.Listeners;
import org.testng.annotations.Test;
import com.aventstack.extentreports.ExtentTest;
import rbs.common.AppiumRepo;
import rbs.common.YamlLoader;
import rbs.MyProject.*;
import rbs.page.LoginPage;

public class MyTestScript extends MobileExecutor {
	YamlLoader yamlLoader = new YamlLoader();
	

	@Test
	public void verifyUserId(){
		try{
			Reporter.log("===============Start verifyingLoginPage========================"+"<br>");
			LoginPage loginPage = new LoginPage();
			Reporter.log("Step 1. Verifying whether user name field is present or not"+"<br>");
			System.out.println(AppiumRepo.isElementPresent(loginPage.getMobileID()));
			Reporter.log("===============End verifyingLoginPage========================"+"<br>");
		}
		catch(Exception e){
			e.printStackTrace();
		}
	}		

}
