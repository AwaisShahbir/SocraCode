public class FindMax {
    public static int findMax(int[] numbers) {
        if (numbers.length == 0) return -1;
        int maxVal = numbers[0];
        for (int i = 1; i < numbers.length; i++) {
            if (numbers[i] > maxVal) {
                maxVal = numbers[i];
            }
        }
        return maxVal;
    }
}
