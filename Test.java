package com.pages;

import java.awt.Robot;
import java.awt.Toolkit;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.NoSuchElementException;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.Iterator;

import javax.imageio.ImageIO;

import org.apache.commons.io.FileUtils;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.NoAlertPresentException;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.Rectangle;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.support.PageFactory;
import org.openqa.selenium.support.ui.ExpectedCondition;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.FluentWait;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.Wait;
import org.openqa.selenium.support.ui.WebDriverWait;

import com.aventstack.extentreports.ExtentTest;
import com.report.ExtentReportNG;
import com.tests.BaseTest;

public class BasePage {
    private static ThreadLocal<WebDriver> driver = new ThreadLocal<>();
    private ExtentReportNG ern = new ExtentReportNG();

    public BasePage(WebDriver driverInstance) {
        driver.set(driverInstance);
        PageFactory.initElements(driver.get(), this);
    }

    private WebDriver getDriver() {
        return driver.get();
    }

    public boolean SwitchAlert() {
        boolean Flag = false;
        try {
            if (getDriver().switchTo().alert() != null) {
                getDriver().switchTo().alert().accept();
                Flag = true;
            }
        } catch (NoAlertPresentException e) {
        }
        return Flag;
    }

    public void doubleClick(WebElement element, String message) {
        String text = message.replaceAll("\\s+", "");
        String filePath = null;
        try {
            filePath = highlightElement(element, text);
        } catch (Exception e) {
            e.printStackTrace();
        }
        ern.enterLogAndCapture(message, filePath);
        if ((getDriver() != null) && (element != null)) {
            (new Actions(getDriver())).doubleClick(element).build().perform();
        }
    }

    public boolean waitForVisibility(WebElement ele) {
        WebDriverWait wait = new WebDriverWait(getDriver(), Duration.ofSeconds(10));
        return wait.until(ExpectedConditions.visibilityOf(ele)) != null;
    }

    public void click(WebElement ele, String message) {
        String text = message.replaceAll("\\s+", "");
        String filePath = null;
        try {
            filePath = highlightElement(ele, text);
        } catch (Exception e) {
            e.printStackTrace();
        }
        ern.enterLogAndCapture(message, filePath);
        waitForVisibility(ele);
        ele.click();
    }

    public void sendKeys(WebElement ele, String txt, String message) {
        waitForVisibility(ele);
        ele.sendKeys(txt);
        String text = message.replaceAll("\\s+", "");
        String filePath = null;
        try {
            filePath = highlightElement(ele, text);
        } catch (Exception e) {
            e.printStackTrace();
        }
        ern.enterLogAndCapture(message, filePath);
    }

    public String getAttribute(WebElement ele, String attribute, String message) {
        String text = message.replaceAll("\\s+", "");
        String filePath = null;
        try {
            filePath = highlightElement(ele, text);
        } catch (Exception e) {
            e.printStackTrace();
        }
        ern.enterLogAndCapture(message, filePath);
        return ele.getAttribute(attribute);
    }

    public void selectDropDownValue(WebElement element, String value) {
        try {
            if (element != null) {
                Select selectBox = new Select(element);
                selectBox.selectByValue(value);
            }
        } catch (NoSuchElementException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public String decryptString(String decryptValue) {
        String result = new String();
        char[] charArray = decryptValue.toChar```java
        charArray();
        for (int i = 0; i < charArray.length; i = i + 2) {
            String st = "" + charArray[i] + "" + charArray[i + 1];
            char ch = (char) Integer.parseInt(st, 16);
            result = result + ch;
        }
        return result;
    }

    public void switchWindow() {
        String parentWindow = getDriver().getWindowHandle();
        Set<String> s = getDriver().getWindowHandles();
        System.out.println("Total Windows::::::::::::" + s.size());
        Iterator<String> I1 = s.iterator();
        while (I1.hasNext()) {
            String child_window = I1.next();
            if (!parentWindow.equals(child_window)) {
                getDriver().switchTo().window(child_window);
            }
        }
        System.out.println(getDriver().getTitle());
    }

    public void switchToParentWindow(String parentWindow) {
        getDriver().switchTo().window(parentWindow);
    }

    public String getCurrentDateAndTime() {
        DateTimeFormatter dtf = DateTimeFormatter.ofPattern("MM/dd/yyyy HH:mm:ss");
        LocalDateTime now = LocalDateTime.now();
        System.out.println(dtf.format(now));
        return dtf.format(now);
    }

    public void waitUntilPageLoad() {
        Wait<WebDriver> wait = new FluentWait<WebDriver>(getDriver()).withTimeout(Duration.ofSeconds(30))
                .pollingEvery(Duration.ofSeconds(5)).ignoring(Exception.class);
        ExpectedCondition<Boolean> documentReady = new ExpectedCondition<Boolean>() {
            @Override
            public Boolean apply(WebDriver driver) {
                JavascriptExecutor js = (JavascriptExecutor) driver;
                String state = (String) js.executeScript("return document.readyState;");
                return state.equals("complete");
            }
        };
        wait.until(documentReady);
    }

    public String highlightElement(WebElement element, String stepName) {
        TakesScreenshot ts = (TakesScreenshot) getDriver();
        for (int i = 0; i < 2; i++) {
            JavascriptExecutor js = (JavascriptExecutor) getDriver();
            js.executeScript("arguments[0].style.border='3px solid orange'", element);
        }
        File source = ts.getScreenshotAs(OutputType.FILE);
        File file = new File(System.getProperty("user.dir") + File.separator + "reports" + File.separator + stepName + ".png");
        try {
            FileUtils.copyFile(source, file);
        } catch (IOException e) {
            e.printStackTrace();
        }
        JavascriptExecutor js = (JavascriptExecutor) getDriver();
        js.executeScript("arguments[0].style.border='0px solid orange'", element);
        return System.getProperty("user.dir") + File.separator + "reports" + File.separator + stepName + ".png";
    }
}




package com.tests;

import java.io.File;
import java.io.IOException;
import java.time.Duration;
import org.apache.commons.io.FileUtils;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import com.pages.LoginPage;
import com.utils.TestData;
import io.github.bonigarcia.wdm.WebDriverManager;

/*
 * Developed by Baxter @Webtestops
 * Resource Name - Reddy Pramodh
 * Date: 11th March 2024
 * Last Code Checkin - 11th March 2024
 * This is Baxter Proprietary Framework - Don't use without any permissions
 * Modified By - Reddy Pramodh
 */

public class BaseTest {
    public static String environment = System.getProperty("environment");
    public static String browserName = System.getProperty("browser");
    TestData td = new TestData();
    private static ThreadLocal<WebDriver> driver = new ThreadLocal<>();
    public LoginPage lp;

    public static WebDriver getDriver() {
        return driver.get();
    }

    public static void setDriver(WebDriver driverInstance) {
        driver.set(driverInstance);
    }

    public void initializeDriver() throws IOException {
        WebDriver webDriver = null;

        // Initialize WebDriver based on the specified browser
        if (browserName.equalsIgnoreCase("chrome")) {
            ChromeOptions options = new ChromeOptions();
            WebDriverManager.chromedriver().setup();
            if (browserName.contains("headless")) {
                options.addArguments("--headless");
            }
            webDriver = new ChromeDriver(options);
        } else if (browserName.equalsIgnoreCase("firefox")) {
            WebDriverManager.firefoxdriver().setup();
            webDriver = new FirefoxDriver();
        } else if (browserName.equalsIgnoreCase("edge")) {
            WebDriverManager.edgedriver().setup();
            webDriver = new EdgeDriver();
        } else {
            throw new IllegalArgumentException("Browser not supported: " + browserName);
        }

        // Set implicit wait and maximize window
        webDriver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));
        webDriver.manage().window().maximize();
        setDriver(webDriver);
    }

    public String getScreenshot(String testCaseName) throws IOException {
        TakesScreenshot ts = (TakesScreenshot) getDriver();
        File source = ts.getScreenshotAs(OutputType.FILE);
        String screenshotPath = System.getProperty("user.dir") + File.separator + "reports" + File.separator + testCaseName + ".png";
        FileUtils.copyFile(source, new File(screenshotPath));
        return screenshotPath;
    }

    @BeforeMethod(alwaysRun = true)
    public LoginPage launchBrowser() throws IOException {
        initializeDriver();
        lp = new LoginPage();
        lp.goTo();
        return lp;
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        WebDriver driverInstance = getDriver();
        if (driverInstance != null) {
            driverInstance.quit();
            driver.remove(); // Clean up ThreadLocal variable
        }


        Here's a prompt for Copilot to create a PowerPoint presentation positioning your BDD Test Generator as an alternative to the licensed Algo QA tool:

```
Create a 6-slide PowerPoint presentation about a Chrome extension called "BDD Test Generator" that serves as an open-source alternative to the licensed Algo QA tool, with the following structure:

Slide 1: Title Slide
- Title: BDD Test Generator Chrome Extension
- Subtitle: A Cost-Effective Alternative to Algo QA for Automated Test Generation
- Include visuals suggesting cost savings and automation testing

Slide 2: Market Challenge
- Title: The Testing Automation Challenge
- Bullet points describing the current market situation:
  - Licensed tools like Algo QA are expensive with per-user licensing costs
  - Organizations need cost-effective testing solutions without compromising quality
  - Technical barriers limit test automation adoption across teams
  - Maintaining test scripts requires specialized knowledge
  - Integration with existing frameworks is often complex

Slide 3: Our Solution
- Title: BDD Test Generator: The Open Alternative
- Describe how the Chrome extension provides similar functionality to Algo QA:
  - Records user interactions in real-time just like premium tools
  - Generates industry-standard Gherkin feature files compatible with any BDD framework
  - Creates ready-to-use Java step definitions that work with existing test infrastructure
  - Supports all common interaction types: navigation, clicks, inputs, dropdowns, checkboxes, radio buttons, and calendar date selections
  - No licensing fees or user limits

Slide 4: Feature Comparison
- Title: Feature Comparison
- Create a comparison table between BDD Test Generator and Algo QA:
  | Feature                      | BDD Test Generator | Algo QA |
  |-----------------------------|-------------------|---------|
  | Real-time recording         | ✓                | ✓       |
  | Gherkin generation          | ✓                | ✓       |
  | Java code generation        | ✓                | ✓       |
  | Smart element detection     | ✓                | ✓       |
  | Calendar handling           | ✓                | ✓       |
  | Credential field handling   | ✓                | ✓       |
  | Cost                        | Free             | Licensed|
  | User limits                 | None             | Per user|
  | Installation                | Simple           | Complex |
  | Customization               | Open source      | Limited |

Slide 5: Implementation Benefits
- Title: Implementation Benefits
- Bullet points highlighting advantages over Algo QA:
  - Zero licensing costs for unlimited users
  - Simple browser-based installation with no server setup
  - Seamless integration with existing Cucumber/Selenium frameworks
  - Full access to source code for customization
  - Community-driven development and support
  - No vendor lock-in
  - Lightweight with minimal resource requirements

Slide 6: Getting Started
- Title: Getting Started Today
- Simple steps to implement:
  1. Install the BDD Test Generator Chrome extension
  2. Record your test scenarios with a single click
  3. Export Gherkin and Java code
  4. Integrate with your existing test framework
  5. Run tests and enjoy the cost savings
- Call to action: "Start automating your tests today without the licensing costs"
- Contact information for support and customization

Please create this presentation with a professional design, appropriate visuals, and animations. Use a color scheme that suggests innovation and cost-effectiveness.
```

This prompt positions your BDD Test Generator as a cost-effective, open-source alternative to the licensed Algo QA tool, highlighting the similar functionality but without the licensing costs and restrictions. The presentation focuses on the value proposition of your extension compared to a commercial product, emphasizing the cost savings and flexibility benefits.
    }
}
