/**
 * Auteur    : Moret Jérôme
 * Date      : 14/03/2017
 * Version   : 1.0
 */

public abstract class Animal {

    String name;

    public Animal(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    abstract public void speak();
}
