package rbs.MyProject;

import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.UnknownHostException;
import java.util.HashMap;

import org.testng.annotations.AfterTest;
import org.apache.commons.io.FileUtils;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeTest;

import com.aventstack.extentreports.ExtentReports;
import com.aventstack.extentreports.reporter.ExtentSparkReporter;

import rbs.common.AppiumRepo;
import rbs.common.YamlLoader;

import org.testng.annotations.BeforeMethod;


public class MobileExecutor {
	static YamlLoader yamlLoader = new YamlLoader();
	static ExtentReports extent;

	@BeforeTest(alwaysRun = true)
	public static ExtentReports extentReportGenerator()
	{
		String path=System.getProperty("user.dir")+"\\reports\\index.html";
		ExtentSparkReporter reporter = new ExtentSparkReporter(path);
		reporter.config().setReportName("Web Automation Results");
		reporter.config().setDocumentTitle("Test Results");

		extent = new ExtentReports();
		extent.attachReporter(reporter);
		extent.setSystemInfo("Tester", "Reddy Pramodh Adalam");
		try {
			BeforeTest();
		} catch (Throwable e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	
		return extent;
	}
	
	public static void BeforeTest() throws Throwable
	{
		System.out.println("TestCase Starts");
		HashMap<String, String> propMap = yamlLoader.getPropertyHashMap();
		try {
			AppiumRepo.startAppium(propMap.get("platform"));
		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@AfterTest(alwaysRun = true)
	public void AfterTest()
	{
		System.out.println("TestCase Ends");
		AppiumRepo.driver.quit();

	}
	
	public String getScreenshotPath(String testCaseName, WebDriver driver) throws IOException
	{
		TakesScreenshot ts = (TakesScreenshot) driver;
		File ss = ts.getScreenshotAs(OutputType.FILE);
		String destPath = System.getProperty("user.dir")+"\\Screenshots\\"+testCaseName+".png";
		File file = new File(destPath);
		FileUtils.copyFile(ss, file);
		return destPath;
	}
	

}
