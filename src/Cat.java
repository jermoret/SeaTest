/**
 * Auteur    : Moret Jérôme
 * Date      : 14/03/2017
 * Version   : 1.0
 */

public class Cat extends Animal {

    public Cat(String name, String color) {
        super(name, color);
    }

    @Override
    public void speak() {
        System.out.println("Meow !");
    }
}
