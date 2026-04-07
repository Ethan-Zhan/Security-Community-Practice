package Solution128;

import javafx.util.Pair;

import java.util.*;

public class Main {
    public static void main(String[] args) {
        Solution solution = new Solution();
        int[] nums = {1,0,1,2};
        System.out.println(solution.longestConsecutive(nums)); // Output: 4
    }
}

class Solution {
    public int longestConsecutive(int[] nums) {
        HashSet<Integer> set = new HashSet<>();
        for (int num : nums) {
            set.add(num);
        }
        int maxLength = 0;
        for (int value : set) {
            if (!set.contains(value - 1)) {
                int currentNum = value;
                int currentLength = 1;
                while (set.contains(currentNum + 1)) {
                    currentNum++;
                    currentLength++;
                }
                maxLength = Math.max(maxLength, currentLength);
            }
        }
        return maxLength;
    }

}