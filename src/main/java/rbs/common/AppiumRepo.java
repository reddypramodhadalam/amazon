package rbs.common;

import java.awt.AWTException;
import java.awt.Robot;
import java.awt.event.KeyEvent;
import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import org.openqa.selenium.By;
import org.openqa.selenium.Dimension;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.NoAlertPresentException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxProfile;
import org.openqa.selenium.ie.InternetExplorerDriver;
import org.openqa.selenium.interactions.Action;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.remote.DesiredCapabilities;
import io.appium.java_client.AppiumDriver;
import io.appium.java_client.TouchAction;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;

public class AppiumRepo {

	public static WebElement webelement;
	public static List<WebElement> webelements = null;
	public static WebDriver driver = null;
	public static int defaultBrowserTimeOut = 30;
	public static List<String> windowHandlers;

	public static WebDriver startAppium(String platformName) throws MalformedURLException {

		if (platformName.equalsIgnoreCase("Android")) {

			DesiredCapabilities cap = new DesiredCapabilities();
			cap.setCapability("platformName", "Android");
			cap.setCapability("platformVersion", "9.0");
			cap.setCapability("udid", "abcd1234");
			cap.setCapability("deviceName", "Galaxy S8");
			cap.setCapability("appPackage", "in.amazon.mShop.android.shopping");
			cap.setCapability("appActivity", "com.amazon.identity.auth.device.AuthPortalUIActivity");
			cap.setCapability("noReset", true);
			cap.setCapability("newCommandTimeout", "1200");
			driver = new AndroidDriver<WebElement>(new URL("http://127.0.0.1:4723/wd/hub"), cap);

		} else if (platformName.equalsIgnoreCase("iOS")) {
			DesiredCapabilities cap = new DesiredCapabilities();
			cap.setCapability("platformName", "iOS");
			cap.setCapability("platformVersion", "11.0");
			cap.setCapability("deviceName", "iPhone 7");
			cap.setCapability("noReset", true);
			cap.setCapability("newCommandTimeout", "1200");
			driver = new IOSDriver<WebElement>(new URL("http://127.0.0.1:4723/wd/hub"), cap);
		}
		return driver;

	}

	public static boolean SwitchAlert() {
		boolean Flag = false;

		try {
			if (driver.switchTo().alert() != null) {
				driver.switchTo().alert().accept();
				Flag = true;
			}

		}

		catch (NoAlertPresentException e) {

		}
		return Flag;

	}

	public static void shutDownDriver() {
		if (driver != null)
			driver.quit();
	}

	public static WebDriver getWebDriver() {
		return driver;
	}

	public static void deleteTempFile() throws UnknownHostException {
		String property = "java.io.tmpdir";
		String temp = System.getProperty(property);
		File directory = new File(temp);
		try {
			delete(directory);
		} catch (IOException e) {
			e.printStackTrace();
			System.exit(0);
		}
	}

	public static void delete(File file) throws IOException {
		if (file.isDirectory()) { // directory is empty, then delete it
			if (file.list().length == 0) {
				file.delete();
			} else {
				// list all the directory contents
				String files[] = file.list();
				for (String temp : files) {
					// construct the file structure
					File fileDelete = new File(file, temp);
					// recursive delete
					delete(fileDelete);
				}
				// check the directory again, if empty then delete it
				if (file.list().length == 0) {
					file.delete();
					System.out.println("Directory is deleted : " + file.getAbsolutePath());
				}
			}
		} else {
			// if file, then delete it
			file.delete();
		}
	}

	public static WebElement findElement(String locator) {

		// Locator Values are Expected in string format like "name==abc" or
		// "id==pqr" or "xpath==//*[@id='uname']"

		if (locator != null) {
			String[] arrLocator = locator.split("==");
			String locatorTag = arrLocator[0].trim();
			String objectLocator = arrLocator[1].trim();
			try {
				if (locatorTag.equalsIgnoreCase("id")) {
					webelement = driver.findElement(By.id(objectLocator));
				} else if (locatorTag.equalsIgnoreCase("name")) {
					webelement = driver.findElement(By.name(objectLocator));
				} else if (locatorTag.equalsIgnoreCase("xpath")) {
					webelement = driver.findElement(By.xpath(objectLocator));
				} else if (locatorTag.equalsIgnoreCase("linkText")) {
					webelement = driver.findElement(By.linkText(objectLocator));
				} else if (locatorTag.equalsIgnoreCase("class")) {
					webelement = driver.findElement(By.className(objectLocator));
				} else if (locatorTag.equalsIgnoreCase("css")) {
					webelement = driver.findElement(By.cssSelector(objectLocator));
				} else {
					String error = "Please Check the Given Locator Syntax :" + locator;
					error = error.replaceAll("'", "\"");

					return null;
				}
			} catch (Exception exception) {
				String error = "Please Check the Given Locator Syntax :" + locator;
				error = error.replaceAll("'", "\"");
				exception.printStackTrace();
				return null;
			}
		}
		return webelement;
	}

	public static void doubleClick(WebElement element) {
		if ((driver != null) && (element != null))
			(new Actions(driver)).doubleClick(element).build().perform();
	}

	public static boolean isElementPresent(String locator) {
		List<WebElement> arrElements = null;
		arrElements = AppiumRepo.findElements(locator);
		if (arrElements.size() > 0 && arrElements != null) {

			return true;
		} else
			System.out.println("Element not found");

		return false;
	}

	public static void ElementWait(String Locator) throws InterruptedException {

		WebElement element = null;
		for (int i = 0; i < 60; i++) {
			try {
				element = AppiumRepo.findElement(Locator);

			} catch (Exception e) {
			}

			if (element != null || element != null)
				return;
			Thread.sleep(3000);
			System.out.println("Waiting");
		}
	}

	public static void WaitForLoad(int TimeMillSec) throws InterruptedException {

		Thread.sleep(TimeMillSec);
	}

	public static List<WebElement> findElements(String locator) {

		if (locator != null) {
			String[] arrLocator = locator.split("==");
			String locatorTag = arrLocator[0].trim();
			String objectLocator = arrLocator[1].trim();

			if (locatorTag.equalsIgnoreCase("id")) {
				webelements = driver.findElements(By.id(objectLocator));
			} else if (locatorTag.equalsIgnoreCase("name")) {
				webelements = driver.findElements(By.name(objectLocator));
			} else if (locatorTag.equalsIgnoreCase("xpath")) {
				webelements = driver.findElements(By.xpath(objectLocator));
			} else if (locatorTag.equalsIgnoreCase("linkText")) {
				webelements = driver.findElements(By.linkText(objectLocator));
			} else if (locatorTag.equalsIgnoreCase("class")) {
				webelements = driver.findElements(By.className(objectLocator));
			} else {
				System.out.println("Please Check the Locator Syntax Given :" + locator);
				return null;
			}
		}
		return webelements;
	}

	public static void mousehovering(String locator) {

		WebElement mouseOverElement = findElement(locator);
		Actions builder = new Actions(driver); // Configure the Action
		Action mouseOver = builder.moveToElement(mouseOverElement).build(); // Get
																			// the
																			// action
		mouseOver.perform(); // Execute the Action
	}

	public static void PressShiftTab() throws AWTException {
		Robot robot = new Robot();
		robot.delay(3000);
		robot.keyPress(KeyEvent.VK_SHIFT);
		robot.keyPress(KeyEvent.VK_TAB);
		robot.keyRelease(KeyEvent.VK_TAB);
		robot.keyRelease(KeyEvent.VK_SHIFT);
	}

	public static void PressTab() throws AWTException {
		Robot robot = new Robot();
		robot.delay(3000);

		robot.keyPress(KeyEvent.VK_TAB);
		robot.keyRelease(KeyEvent.VK_TAB);

	}

	public static String getAttribute(String locator, String attributeName) {
		String attributeValue = null;
		try {

			WebElement element = AppiumRepo.findElement(locator);
			if (element != null)
				attributeValue = element.getAttribute(attributeName);
			element = null;
		} catch (Exception e) {
			e.printStackTrace();
		}

		return attributeValue;
	}

	public static void clearElement(String locator) {
		try {

			WebElement element = AppiumRepo.findElement(locator);
			element.clear();
			element = null;
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	public static void enterText(String locator, String value) {

		try {

			WebElement element = AppiumRepo.findElement(locator);
			element.sendKeys(value);
			element = null;
		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	public static void click(String locator) {
		try {
			WebElement element = AppiumRepo.findElement(locator);
			if (element != null)
				element.click();
			else
				System.out.println("Element Is NULL");
			element = null;

		} catch (Exception e) {
			System.out.println(" Error occured whlie click on the element " + locator + " *** " + e.getMessage());

		}

	}

	public static String getElementText(String locator) {
		WebElement element;
		String text = null;
		try {
			element = AppiumRepo.findElement(locator);
			if (element != null)

				text = element.getText();

		} catch (Exception e) {
			e.printStackTrace();
		}
		element = null;

		return text;
	}

	public static void driverInitialize(WebDriver webDriver) {
		AppiumRepo.driver = webDriver;
	}

	/**
	 * 
	 * Below code is for swipe functionality
	 */
	public static void swipeVertical(AppiumDriver driver, double startPercentage, double finalPercentage,
			double anchorPercentage, int duration) throws Exception {
		Dimension size = driver.manage().window().getSize();
		int anchor = (int) (size.width * anchorPercentage);
		int startPoint = (int) (size.height * startPercentage);
		int endPoint = (int) (size.height * finalPercentage);
		new TouchAction(driver).press(anchor, startPoint).waitAction(duration).moveTo(anchor, endPoint).release()
				.perform();
	}

	public static void swipeHorizontal(AppiumDriver driver, double startPercentage, double finalPercentage,
			double anchorPercentage, int duration) throws Exception {
		Dimension size = driver.manage().window().getSize();
		int anchor = (int) (size.height * anchorPercentage);
		int startPoint = (int) (size.width * startPercentage);
		int endPoint = (int) (size.width * finalPercentage);
		new TouchAction(driver).press(startPoint, anchor).waitAction(duration).moveTo(endPoint, anchor).release()
				.perform();
	}

}
