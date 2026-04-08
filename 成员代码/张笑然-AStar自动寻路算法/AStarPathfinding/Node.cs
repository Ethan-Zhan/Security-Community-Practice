using System;

namespace AStarPathfinding
{
    public class Node
    {
        public int x;
        public int y;
        public bool walkable;

        public int gCost; // 起点到当前点
        public int hCost; // 启发式估价
        public int fCost; // 总成本

        public Node parent;

        public Node(int x, int y, bool walkable)
        {
            this.x = x;
            this.y = y;
            this.walkable = walkable;
        }

        public void CalculateFCost()
        {
            fCost = gCost + hCost;
        }

        public override string ToString()
        {
            return $"({x},{y})";
        }
    }
}
