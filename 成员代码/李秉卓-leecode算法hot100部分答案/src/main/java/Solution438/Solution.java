package Solution438;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public List<Integer> findAnagrams(String s, String p) {
        char[] target = p.toCharArray();
        Arrays.sort(target);
        int left = 0;
        int right = p.length();
        List<Integer> result = new ArrayList<>();
        while (right < s.length() + 1) {
            String tmp = s.substring(left, right);
            char[] tmpArr = tmp.toCharArray();
            Arrays.sort(tmpArr);
            if (Arrays.equals(tmpArr, target)) {
                result.add(left);
            }
            left++;
            right++;
        }
        return result;

    }
}