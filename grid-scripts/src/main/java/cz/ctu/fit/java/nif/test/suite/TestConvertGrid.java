
package cz.ctu.fit.java.nif.test.suite;

/**
 *
 * @author Milan Dojchinovski <milan.dojchinovski@fit.cvut.cz>
 * http://dojchinovski.mk
 */
public class TestConvertGrid {
    public static void main(String[] args) {
        
        // 1) data location, 2) output location - /Users/Milan/Desktop/grid/
        System.out.println("The script takes two parameters.\n"
                + "The first is the data location e.g., /Users/Milan/Desktop/grid/grid.json"
                + "The second is the output location, e.g., /Users/Milan/Desktop/grid/");
        
        System.out.println("Data location: " + args[0]);
        System.out.println("Output location: " + args[1]);
        new GridConverter().convert("/Users/Milan/Desktop/grid/grid.json", "/Users/Milan/Desktop/grid/" );
//        new GridConverter().convert("/Users/Milan/Desktop/grid/grid.json", "/Users/Milan/Desktop/grid/" );
    }
}
