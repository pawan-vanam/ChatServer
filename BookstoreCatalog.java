import javax.swing.JFrame;
import javax.swing.JTree;
import javax.swing.SwingUtilities;
import javax.swing.tree.DefaultMutableTreeNode;

/**
 * A Java Swing application that displays a bookstore catalog using a JTree.
 * The entire GUI is constructed using only the JTree component within a JFrame.
 */
public class BookstoreCatalog extends JFrame {

    private final JTree tree;

    public BookstoreCatalog() {
        // Create the root node for the tree
        DefaultMutableTreeNode root = new DefaultMutableTreeNode("Bookstore");

        // --- Categories (Level 1) ---
        DefaultMutableTreeNode fiction = new DefaultMutableTreeNode("Fiction");
        DefaultMutableTreeNode nonFiction = new DefaultMutableTreeNode("Non-Fiction");
        DefaultMutableTreeNode scienceTech = new DefaultMutableTreeNode("Science & Technology");
        DefaultMutableTreeNode childrens = new DefaultMutableTreeNode("Children’s Books");
        DefaultMutableTreeNode comicsManga = new DefaultMutableTreeNode("Comics & Manga");
        DefaultMutableTreeNode academic = new DefaultMutableTreeNode("Academic & Education");

        // Add categories to the root node
        root.add(fiction);
        root.add(nonFiction);
        root.add(scienceTech);
        root.add(childrens);
        root.add(comicsManga);
        root.add(academic);

        // --- Authors and Books (Level 2 & 3) with Details (Level 4) ---

        // 1. Fiction Authors
        addAuthorWithBooks(fiction, "J.K. Rowling", new String[]{
            "Harry Potter and the Sorcerer’s Stone",
            "Harry Potter and the Chamber of Secrets",
            "Harry Potter and the Prisoner of Azkaban"
        }, getBookDetails(1));

        addAuthorWithBooks(fiction, "George R.R. Martin", new String[]{
            "A Game of Thrones",
            "A Clash of Kings"
        }, getBookDetails(2));

        addAuthorWithBooks(fiction, "Agatha Christie", new String[]{
            "And Then There Were None",
            "Murder on the Orient Express"
        }, getBookDetails(3));


        // 2. Science & Technology Authors
        addAuthorWithBooks(scienceTech, "Stephen Hawking", new String[]{
            "A Brief History of Time",
            "The Grand Design",
            "Black Holes and Baby Universes"
        }, getBookDetails(4));

        addAuthorWithBooks(scienceTech, "Elon Musk (biographies)", new String[]{
            "Elon Musk: Tesla, SpaceX, and the Quest for a Fantastic Future"
        }, getBookDetails(5));

        addAuthorWithBooks(scienceTech, "Brian Greene", new String[]{
            "The Elegant Universe",
            "The Fabric of the Cosmos"
        }, getBookDetails(6));

        // 3. Non-Fiction Authors
        addAuthorWithBooks(nonFiction, "Yuval Noah Harari", new String[]{
            "Sapiens: A Brief History of Humankind",
            "Homo Deus: A Brief History of Tomorrow"
        }, getBookDetails(7));

        addAuthorWithBooks(nonFiction, "Michelle Obama", new String[]{
            "Becoming"
        }, getBookDetails(8));

        // 4. Children's Books Authors
        addAuthorWithBooks(childrens, "Dr. Seuss", new String[]{
            "The Cat in the Hat",
            "Green Eggs and Ham"
        }, getBookDetails(9));
        
        addAuthorWithBooks(childrens, "Eric Carle", new String[]{
            "The Very Hungry Caterpillar"
        }, getBookDetails(10));

        // 5. Comics & Manga Authors
        addAuthorWithBooks(comicsManga, "Stan Lee", new String[]{
            "The Amazing Spider-Man, Epic Collection: Great Power",
            "The Incredible Hulk Epic Collection: Man or Monster?"
        }, getBookDetails(11));

        addAuthorWithBooks(comicsManga, "Hajime Isayama", new String[]{
            "Attack on Titan, Vol. 1"
        }, getBookDetails(12));

        // 6. Academic & Education Authors
        addAuthorWithBooks(academic, "Eric R. Kandel", new String[]{
            "Principles of Neural Science, Fifth Edition"
        }, getBookDetails(13));
        
        addAuthorWithBooks(academic, "Paul A. Tipler", new String[]{
            "Physics for Scientists and Engineers, 6th Edition"
        }, getBookDetails(14));

        // Create the JTree component with the root node
        tree = new JTree(root);
        
        // Add the tree to the frame
        add(tree);

        // Set frame properties
        this.setTitle("Bookstore Catalog");
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.setSize(400, 600);
        this.setLocationRelativeTo(null); // Center the frame
        this.setVisible(true);
    }

    /**
     * Helper method to add an author and their books to a category node.
     *
     * @param categoryNode The parent node for the author.
     * @param authorName   The name of the author.
     * @param bookTitles   An array of book titles by the author.
     * @param details      A 2D array of book details.
     */
    private void addAuthorWithBooks(DefaultMutableTreeNode categoryNode, String authorName, String[] bookTitles, String[][] details) {
        DefaultMutableTreeNode authorNode = new DefaultMutableTreeNode(authorName);
        categoryNode.add(authorNode);

        for (int i = 0; i < bookTitles.length; i++) {
            DefaultMutableTreeNode bookNode = new DefaultMutableTreeNode(bookTitles[i]);
            authorNode.add(bookNode);
            if (i < details.length) {
                addBookDetails(bookNode, details[i]);
            }
        }
    }

    /**
     * Helper method to add book details as leaf nodes to a book node.
     *
     * @param bookNode The parent book node.
     * @param details  An array of details for the book.
     */
    private void addBookDetails(DefaultMutableTreeNode bookNode, String[] details) {
        bookNode.add(new DefaultMutableTreeNode("Price: " + details[0]));
        bookNode.add(new DefaultMutableTreeNode("ISBN: " + details[1]));
        bookNode.add(new DefaultMutableTreeNode("Availability: " + details[2]));
        bookNode.add(new DefaultMutableTreeNode("Publisher: " + details[3]));
        bookNode.add(new DefaultMutableTreeNode("Rating: " + details[4]));
    }
    
    /**
     * Helper method to provide sample book details.
     * @param bookSet A number to select a set of details.
     * @return A 2D string array with book details.
     */
    private String[][] getBookDetails(int bookSet) {
        return switch (bookSet) {
            case 1 -> new String[][]{
                {"$19.99", "978-0747532743", "In Stock", "Bloomsbury", "4.8/5"},
                {"$21.50", "978-0439064873", "In Stock", "Scholastic", "4.7/5"},
                {"$22.99", "978-0439136365", "Out of Stock", "Scholastic", "4.9/5"}
            };
            case 2 -> new String[][]{
                {"$18.95", "978-0553381689", "In Stock", "Bantam Spectra", "4.6/5"},
                {"$19.95", "978-0553381696", "In Stock", "Bantam Spectra", "4.5/5"}
            };
            case 3 -> new String[][]{
                {"$14.99", "978-0312330873", "In Stock", "St. Martin's Press", "4.7/5"},
                {"$15.50", "978-0062073501", "Out of Stock", "William Morrow", "4.8/5"}
            };
            case 4 -> new String[][]{
                {"$24.95", "978-0553380169", "In Stock", "Bantam", "4.7/5"},
                {"$23.50", "978-0553386226", "In Stock", "Bantam", "4.6/5"},
                {"$20.00", "978-0553370737", "In Stock", "Bantam", "4.5/5"}
            };
            case 5 -> new String[][]{
                {"$17.00", "978-0062301239", "In Stock", "Ecco", "4.6/5"}
            };
            case 6 -> new String[][]{
                {"$18.00", "978-0393337912", "Out of Stock", "W. W. Norton", "4.5/5"},
                {"$19.50", "978-0375713444", "In Stock", "Vintage", "4.6/5"}
            };
            case 7 -> new String[][]{
                {"$22.50", "978-0062316097", "In Stock", "Harper", "4.7/5"},
                {"$24.00", "978-0062464316", "In Stock", "Harper", "4.6/5"}
            };
            case 8 -> new String[][]{
                {"$20.00", "978-1524763138", "In Stock", "Crown", "4.9/5"}
            };
            case 9 -> new String[][]{
                {"$9.99", "978-0394800011", "In Stock", "Random House", "4.9/5"},
                {"$10.50", "978-0394800165", "In Stock", "Random House", "4.8/5"}
            };
            case 10 -> new String[][]{
                {"$11.99", "978-0399226908", "In Stock", "Philomel Books", "4.9/5"}
            };
            case 11 -> new String[][]{
                {"$39.99", "978-1302906950", "In Stock", "Marvel", "4.8/5"},
                {"$34.99", "978-0785195449", "Out of Stock", "Marvel", "4.7/5"}
            };
            case 12 -> new String[][]{
                {"$10.99", "978-1612620244", "In Stock", "Kodansha Comics", "4.7/5"}
            };
            case 13 -> new String[][]{
                {"$150.00", "978-0071390118", "In Stock", "McGraw-Hill Education", "4.8/5"}
            };
            case 14 -> new String[][]{
                {"$250.00", "978-1429201247", "Out of Stock", "W. H. Freeman", "4.5/5"}
            };
            default -> new String[][]{{"N/A", "N/A", "N/A", "N/A", "N/A"}};
        }; // J.K. Rowling
        // George R.R. Martin
        // Agatha Christie
        // Stephen Hawking
        // Elon Musk
        // Brian Greene
        // Yuval Noah Harari
        // Michelle Obama
        // Dr. Seuss
        // Eric Carle
        // Stan Lee
        // Hajime Isayama
        // Eric R. Kandel
        // Paul A. Tipler
    }


    /**
     * The main method to run the application.
     *
     * @param args Command line arguments (not used).
     */
    public static void main(String[] args) {
        // Ensure the GUI is created on the Event Dispatch Thread
        SwingUtilities.invokeLater(() -> new BookstoreCatalog());
    }
}

