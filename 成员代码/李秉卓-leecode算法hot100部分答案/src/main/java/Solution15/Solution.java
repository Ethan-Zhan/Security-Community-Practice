package Solution15;

import java.util.*;

class Solution {
    public List<List<Integer>> threeSum(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> result = new ArrayList<>();
        for (int first = 0; first < nums.length; first++) {
            if (first > 0 && nums[first] == nums[first - 1]) {
                continue; // Skip duplicate first elements
            }
            int second = first + 1;
            int third = nums.length - 1;
            while (second < third) {
                int sum = nums[first] + nums[second] + nums[third];
                if (sum < 0) {
                    second++;
                } else if (sum > 0) {
                    third--;
                } else {
                    result.add(Arrays.asList(nums[first], nums[second], nums[third]));
                    while (second < third && nums[second] == nums[second + 1]) {
                        second++; // Skip duplicate second elements
                    }
                    while (second < third && nums[third] == nums[third - 1]) {
                        third--; // Skip duplicate third elements
                    }
                    second++;
                    third--;
                }
            }
        }
        return result;

    }
}
