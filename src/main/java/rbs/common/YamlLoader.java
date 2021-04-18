package rbs.common;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.Properties;

public class YamlLoader {
	String strPropval;
	
	public String getPropertyValue(String propName) throws Throwable {
		Properties pro = new Properties();
		FileInputStream in;
		
		try {
			in = new FileInputStream(System.getProperty("user.dir")+File.separator+"ExternalFiles"+File.separator+"testData.yaml");
			pro.load(in);
			strPropval = pro.getProperty(propName);
		} catch (FileNotFoundException e){
			e.printStackTrace();
		}
		return strPropval;
	}
	
	public HashMap<String, String> getPropertyHashMap() throws Throwable {
		HashMap<String, String> propMap = new HashMap<String, String>();
		Properties pro = new Properties();
		FileInputStream in;
		try {
			in = new FileInputStream(System.getProperty("user.dir")+File.separator+"ExternalFiles"+File.separator+"testData.yaml");
			pro.load(in);
			for (String key: pro.stringPropertyNames()){
				String value = pro.getProperty(key).trim();
				propMap.put(key, value);
			}
		} catch (FileNotFoundException e){
			e.printStackTrace();
		}
		return propMap;
	}
}
