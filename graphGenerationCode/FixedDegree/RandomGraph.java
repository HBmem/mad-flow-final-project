//Zane,Yogi,Nick,Jodie
//TCSS 543
//Nov. 21, 08

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.*;

public class RandomGraph {

	private static final String NL = "\n";

	/**
	 * Entrance point for the program.
	 * Can be run with command-line arguments or will prompt for input if none provided.
	 * @param args - [v, e, min, max, f] where:
	 *   v - the number of vertices
	 *   e - the number of edges leaving each node
	 *   min - the lower bound on the edge capacities
	 *   max - the upper bound on the edge capacities
	 *   f - path and file name for saving the graph
	 */
	public static void main(String[] args) throws Exception{
		int vertices, edges, minCapacity, maxCapacity;
		String fileName;

		if(args.length == 5){
			// Use command-line arguments
			vertices = Integer.parseInt(args[0]);
			edges = Integer.parseInt(args[1]);
			minCapacity = Integer.parseInt(args[2]);
			maxCapacity = Integer.parseInt(args[3]);
			fileName = args[4];
		}else{
			// Prompt for input
			System.out.println("\n\n---------------------------------------------------");
			System.out.print("Enter number of vertices: \t\t\t");
			vertices = GetInt();
			System.out.print("Enter number of edges leaving each node: \t");
			edges = GetInt();
			System.out.print("Enter minimum capacity: \t\t\t");
			minCapacity = GetInt();
			System.out.print("Enter maximum capacity: \t\t\t");
			maxCapacity = GetInt();
			System.out.print("Enter output file name (without .txt): \t");
			fileName = GetString() + ".txt";
			System.out.println("---------------------------------------------------\n");
		}

		if(vertices > edges){
			if(maxCapacity >= minCapacity){
				toFile(graphBuilder(vertices, edges, minCapacity, maxCapacity), fileName);
				System.out.println("\nDONE!");
			}else{
				System.out.println("\nFAIL!");
				System.out.println("Max must be greater than or equal to min.");
			}
		}else{
			System.out.println("\nFAIL!");
			System.out.println("The number of vertices must exceed the number of edges leaving each node.");
		}
	}

	/**
	 * This method creates a 3 token representation of a graph.
	 * @param v The number of vertices in the graph
	 * @param e The number of edges leaving each vertice
	 * @param min The lowerbound on the capacity value of each edge
	 * @param max The upperbound on the capacity value of each edge
	 * @return A string buffer, each line contains 3 tokens corresponding
	 *			to a directed edge: the tail, the head, and the capacity.
	 */
	public static StringBuffer graphBuilder(int v, int e, int min, int max){
		int i;
		int j;
		int head;
		int c;
		SortedSet s;
		Random gen = new Random();
		StringBuffer bfr = new StringBuffer();

		//Add distinguished node s
		j = 1;
		s = new TreeSet();
		while(j <= e){
			head = gen.nextInt(v) + 1;
			if(!s.contains(head)){
				s.add(head);
				c = min + gen.nextInt(max - min + 1);
				bfr.append("s"+" "+"v"+head+" "+c+NL);
				j++;
			}
		}

		//Add distinguished node t
		j = 1;
		s = new TreeSet();
		while(j <= e){
			int tail = gen.nextInt(v) + 1;
			if(!s.contains(tail)){
				s.add(tail);
				c = min + gen.nextInt(max - min + 1);
				bfr.append("v"+tail+" "+"t"+" "+c+NL);
				j++;
			}
		}

		//Add internal nodes
		for(i = 1; i <= v; i++){
			s = new TreeSet();
			s.add(i);
			j = 1;
			while(j <= e){
				head = gen.nextInt(v) + 1;
				if(!s.contains(head)){
					s.add(head);
					c = min + gen.nextInt(max - min + 1);
					bfr.append("v"+i+" "+"v"+head+" "+c+NL);
					j++;
				}
			}
		}
		return bfr;
	}


	/**
	 * This method attempts to save a string at a given location.
	 * @param outString The StringBuffer containing the data being saved
	 * @param filename The complete file path including file name
	 */
	private static void toFile(StringBuffer outString, String filename){
		try{
			BufferedWriter fout = new BufferedWriter(new FileWriter(filename));
			fout.write(outString.toString());
			fout.close();
		}catch(Exception e){
			System.out.println("Error saving file.");
			System.out.println("Please check file paths and restart this program.");
			System.exit(1);
		}
	}

	// Helper functions
	public static String GetString() throws IOException {
		BufferedReader stringIn = new BufferedReader(new InputStreamReader(System.in));
		return stringIn.readLine();
	}

	public static int GetInt() throws IOException {
		String aux = GetString();
		return Integer.parseInt(aux);
	}
}
