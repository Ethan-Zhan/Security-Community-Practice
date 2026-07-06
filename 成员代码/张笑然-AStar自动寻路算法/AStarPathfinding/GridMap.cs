using System;
using System.Collections.Generic;
using System.Xml.Linq;

namespace AStarPathfinding
{
    public class GridMap
    {
        private int width;
        private int height;
        private Node[,] grid;
    
        public GridMap(int width, int height)
        {
            this.width = width;
            this.height = height;
    
            grid = new Node[width, height];
    
            // 初始化网格（默认全部可通行）
            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    grid[x, y] = new Node(x, y, true);
                }
            }
        }
    
        public Node GetNode(int x, int y)
        {
            return grid[x, y];
        }
    
        /// <summary>
        /// 获取邻居节点（8方向）
        /// </summary>
        public List<Node> GetNeighbors(Node node)
        {
            List<Node> neighbors = new List<Node>();
    
            for (int dx = -1; dx <= 1; dx++)
            {
                for (int dy = -1; dy <= 1; dy++)
                {
                    if (dx == 0 && dy == 0)
                        continue;
    
                    int x = node.x + dx;
                    int y = node.y + dy;
    
                    if (x >= 0 && x < width && y >= 0 && y < height)
                    {
                        neighbors.Add(grid[x, y]);
                    }
                }
            }
    
            return neighbors;
        }
    }
}
