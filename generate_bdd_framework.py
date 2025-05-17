import os
import json

BASE_DIR = "GeneratedBDDFramework"

def load_json_from_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def make_dirs():
    folders = [
        os.path.join(BASE_DIR, "src", "main", "java", "utils"),
        os.path.join(BASE_DIR, "src", "test", "java", "stepdefs"),
        os.path.join(BASE_DIR, "src", "test", "java", "runners"),
        os.path.join(BASE_DIR, "src", "test", "resources", "features")
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def create_pom():
    pom_content = '''<project xmlns="http://maven.apache.org/POM/4.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                        http://maven.apache.org/xsd/maven-4.0.0.xsd">
      <modelVersion>4.0.0</modelVersion>
      <groupId>com.generated</groupId>
      <artifactId>BDDFramework</artifactId>
      <version>1.0-SNAPSHOT</version>
      <properties>
        <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
      </properties>
      <dependencies>
        <dependency>
          <groupId>org.seleniumhq.selenium</groupId>
          <artifactId>selenium-java</artifactId>
          <version>4.11.0</version>
        </dependency>
        <dependency>
          <groupId>io.cucumber</groupId>
          <artifactId>cucumber-java</artifactId>
          <version>7.12.0</version>
        </dependency>
        <dependency>
          <groupId>io.cucumber</groupId>
          <artifactId>cucumber-testng</artifactId>
          <version>7.12.0</version>
        </dependency>
        <dependency>
          <groupId>org.testng</groupId>
          <artifactId>testng</artifactId>
          <version>7.8.0</version>
          <scope>test</scope>
        </dependency>
        <dependency>
          <groupId>com.aventstack</groupId>
          <artifactId>extentreports</artifactId>
          <version>5.0.9</version>
        </dependency>
        <dependency>
          <groupId>com.google.code.gson</groupId>
          <artifactId>gson</artifactId>
          <version>2.10.1</version>
        </dependency>
        <dependency>
          <groupId>io.github.bonigarcia</groupId>
          <artifactId>webdrivermanager</artifactId>
          <version>5.5.1</version>
        </dependency>
      </dependencies>
      <build>
        <plugins>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <version>3.0.0-M9</version>
            <configuration>
              <includes>
                <include>**/TestRunner.java</include>
              </includes>
            </configuration>
          </plugin>
        </plugins>
      </build>
    </project>'''
    with open(os.path.join(BASE_DIR, "pom.xml"), "w") as f:
        f.write(pom_content)

def create_feature_file(actions, url):
    feature_path = os.path.join(BASE_DIR, "src", "test", "resources", "features", "GeneratedScenario.feature")
    lines = ["Feature: Auto-generated test from JSON actions\n",
             "  Scenario: Run user actions from JSON\n",
             f"    Given I open the application \"{url}\""]
    for act in actions:
        name = act.get("name", "").strip()
        if not name:
            continue
        action_type = act["type"]
        if action_type == "input":
            value = act.get("value", "")
            lines.append(f"    When I input \"{value}\" into \"{name}\"")
        elif action_type in ["click", "button"]:
            lines.append(f"    And I click \"{name}\"")
        else:
            pass

    with open(feature_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Feature file created at {feature_path}")

def create_webdriver_manager():
    content = '''package utils;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import io.github.bonigarcia.wdm.WebDriverManager;

public class WebDriverManager {
    private static WebDriver driver;

    public static WebDriver getDriver() {
        if (driver == null) {
            WebDriverManager.chromedriver().setup();
            driver = new ChromeDriver();
            driver.manage().window().maximize();
        }
        return driver;
    }

    public static void quitDriver() {
        if (driver != null) {
            driver.quit();
            driver = null;
        }
    }
}
'''
    path = os.path.join(BASE_DIR, "src", "main", "java", "utils", "WebDriverManager.java")
    with open(path, "w") as f:
        f.write(content)
    print("WebDriverManager.java created with bonigarcia WebDriverManager")

def create_step_definitions(actions):
    element_map = {}
    for act in actions:
        name = act.get("name", "").strip()
        xpath = act.get("xpath", "")
        if name and xpath:
            element_map[name] = xpath

    content = '''package stepdefs;

import io.cucumber.java.en.*;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import utils.WebDriverManager;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

public class StepDefinitions {

    WebDriver driver = WebDriverManager.getDriver();
    WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));

    Map<String, String> elementMap = new HashMap<String, String>() {{
'''
    for name, xpath in element_map.items():
        content += f'        put("{name}", "{xpath}");\n'
    content += '''    }};

    @Given("I open the application {string}")
    public void i_open_the_application(String url) {
        driver.get(url);
    }

    @When("I input {string} into {string}")
    public void i_input_into(String value, String name) {
        String xpath = elementMap.get(name);
        WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath(xpath)));
        element.clear();
        element.sendKeys(value);
    }

    @When("I click {string}")
    public void i_click(String name) {
        String xpath = elementMap.get(name);
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(By.xpath(xpath)));
        element.click();
    }
}
'''
    path = os.path.join(BASE_DIR, "src", "test", "java", "stepdefs", "StepDefinitions.java")
    with open(path, "w") as f:
        f.write(content)
    print("StepDefinitions.java created")

def create_test_runner():
    content = '''package runners;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;

@CucumberOptions(
    features = "src/test/resources/features",
    glue = {"stepdefs"},
    plugin = {"pretty", "html:target/cucumber-reports.html"},
    monochrome = true
)
public class TestRunner extends AbstractTestNGCucumberTests {
}
'''
    path = os.path.join(BASE_DIR, "src", "test", "java", "runners", "TestRunner.java")
    with open(path, "w") as f:
        f.write(content)
    print("TestRunner.java created")

def create_extent_manager():
    content = '''package utils;

import com.aventstack.extentreports.ExtentReports;
import com.aventstack.extentreports.reporter.ExtentHtmlReporter;

public class ExtentManager {
    private static ExtentReports extent;

    public static ExtentReports getInstance() {
        if (extent == null) {
            ExtentHtmlReporter htmlReporter = new ExtentHtmlReporter("extent-report.html");
            extent = new ExtentReports();
            extent.attachReporter(htmlReporter);
        }
        return extent;
    }
}
'''
    path = os.path.join(BASE_DIR, "src", "main", "java", "utils", "ExtentManager.java")
    with open(path, "w") as f:
        f.write(content)
    print("ExtentManager.java created")

def main():
    # Load JSON file path here
    json_file_path = "actions.json"

    json_data = load_json_from_file(json_file_path)
    make_dirs()
    create_pom()
    create_feature_file(json_data["actions"], json_data["url"])
    create_webdriver_manager()
    create_step_definitions(json_data["actions"])
    create_test_runner()
    create_extent_manager()
    print(f"BDD Framework generated in folder: {BASE_DIR}")

if __name__ == "__main__":
    main()