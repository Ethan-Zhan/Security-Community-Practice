using System;
using System.Collections.Generic;
using System.Xml.Linq;

namespace AStarPathfinding
{
    class Program
    {
        static void Main(string[] args)
        {
            GridMap map = new GridMap(10,10);

            // 设置障碍物
            map.SetObstacle(1,1);
            map.SetObstacle(3,3);
            map.SetObstacle(3,4);
            map.SetObstacle(3,5);
            map.SetObstacle(4,5);
            map.SetObstacle(5,5);
            map.SetObstacle(6,6);

            Node start = map.GetNode(0,0);
            Node end = map.GetNode(8,8);

            AStarPathfinder pathfinder = new AStarPathfinder(map);

            List<Node> path = pathfinder.FindPath(start, end);

            Console.WriteLine("地图路径结果：\n");
            map.PrintMap(path, start, end);

            Console.WriteLine("\n路径点：");
            if (path != null)
            {
                foreach (var node in path)
                {
                    Console.Write(node + " ");
                }
            }
            else
            {
                Console.WriteLine("未找到路径！");
            }

            Console.ReadKey();
        }
    }
}